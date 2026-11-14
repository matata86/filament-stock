"""Filament Stock: grams of filament left per slicer profile, fed by ha-bambulab."""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, is_dataclass
from datetime import timedelta

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.storage import Store

from .const import CONF_LOW, CONF_PRINTER, CONF_SPOOL, CONF_WASTE, DEFAULTS, DOMAIN, SOURCE_PLATFORM
from .logic import FACTS, JobTracker, is_custom, item_label, merge_plan, profile_facts, slot_item
from .panel import async_setup_panel

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.NUMBER]

SCHEMA = 2  # layout of the stored data: items keyed by profile
SYNC_INTERVAL = timedelta(minutes=15)  # how often the user's profiles are read from Bambu Cloud

LOW_MESSAGE = {
    "cs": ("Dochází filament", "{item}: zbývá {grams:.0f} g (práh {low:.0f} g)."),
    "en": ("Filament running low", "{item}: {grams:.0f} g left (threshold {low:.0f} g)."),
}


def _number(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class Stock:
    """Stock of one printer: storage, source entities and the job tracker."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.items: dict[str, float] = {}  # item key -> grams
        # item key -> {'profile', 'brand', 'material', 'color': from the printer; 'name': typed by the user; 'barcodes'}
        self.meta: dict[str, dict] = {}
        self.brands: dict[str, str] = {}  # vendor from the printer -> brand shown ('Smart Print' -> 'PL/SM')
        self.aliases: dict[str, str] = {}  # merged item key -> the item that holds its grams and barcodes
        self.profiles: dict[str, dict] = {}  # profile id -> ha-bambulab filament data
        self.tracker = JobTracker()
        self.signal_new = f"{DOMAIN}_new_{entry.entry_id}"
        self.signal_update = f"{DOMAIN}_update_{entry.entry_id}"
        self._store: Store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}")
        self._printer: dict[str, str] = {}  # translation_key -> entity_id
        self._slots: dict[str, str] = {}  # entity_id -> slot name

    def option(self, key: str) -> float:
        return self.entry.options.get(key, DEFAULTS[key])

    async def async_load(self) -> None:
        data = (await self._store.async_load()) or {}
        if data.get("schema") != SCHEMA:
            # Items used to be material + colour; they cannot be mapped to profiles, start empty.
            ent_reg = er.async_get(self.hass)
            for entity in er.async_entries_for_config_entry(ent_reg, self.entry.entry_id):
                ent_reg.async_remove(entity.entity_id)
            data = {}
        self.items = data.get("items", {})
        self.meta = data.get("meta", {})
        self.brands = data.get("brands", {})
        self.aliases = data.get("aliases", {})

    async def async_sync_profiles(self, _now=None) -> dict | None:
        """Read the user's profiles from Bambu Cloud again and apply new names and items."""
        result = await self.async_load_profiles(cloud=True)
        self.refresh()
        return result

    async def async_load_profiles(self, cloud: bool = False) -> dict | None:
        """Ask ha-bambulab for the profile list; the user's own profiles become items.

        Returns how many own profiles there are, how many are new and how many changed; None on error.
        """
        try:
            if cloud:
                # ha-bambulab reads the cloud profiles only when it connects. Its internals, so guarded.
                device = dr.async_get(self.hass).async_get(self.entry.data[CONF_PRINTER])
                coordinators = self.hass.data.get(SOURCE_PLATFORM, {})
                coordinator = coordinators.get(device.config_entry_id) if device else None
                if settings := getattr(getattr(coordinator, "client", None), "slicer_settings", None):
                    await self.hass.async_add_executor_job(settings.update)
            response = await self.hass.services.async_call(
                SOURCE_PLATFORM,
                "get_filament_data",
                {"device_id": self.entry.data[CONF_PRINTER]},
                blocking=True,
                return_response=True,
            )
        except Exception as err:  # noqa: BLE001 - optional data, the slots still work without it
            _LOGGER.warning("Profile list from ha-bambulab not available: %s", err)
            return None
        # Built-in profiles are dicts, the user's own ones come as a FilamentInfo dataclass.
        profiles = {k: asdict(v) if is_dataclass(v) else v for k, v in (response or {}).items()}
        self.profiles = {k: v for k, v in profiles.items() if isinstance(v, dict) and "name" in v}
        new, renamed = [], 0
        for key, profile in self.profiles.items():
            if is_custom(key) and key not in self.aliases:
                old = self.meta.get(key, {})
                facts = profile_facts(profile)
                if old.get("color"):
                    # A colour seen in a slot beats the guess from the profile name.
                    facts["color"] = old["color"]
                changed = self._learn(key, {**old, **facts})
                if key not in self.items:
                    self.items[key] = 0.0
                    new.append(key)
                else:
                    renamed += bool(changed)
        self._save()
        # During setup the entities do not exist yet, they are created from the items.
        loaded = self.entry.state is ConfigEntryState.LOADED
        if loaded and new:
            async_dispatcher_send(self.hass, self.signal_new, new)
        if loaded and renamed:
            # The name is part of the entities, reload to apply it.
            self.hass.config_entries.async_schedule_reload(self.entry.entry_id)
        own = sum(1 for key in self.profiles if is_custom(key) and key not in self.aliases)
        return {"profiles": own, "new": len(new), "changed": renamed}

    def _learn(self, key: str, facts: dict) -> bool:
        """Store what the printer says about an item; True when it changed."""
        old = self.meta.get(key, {})
        new = {**{k: v for k, v in old.items() if k not in FACTS}, **facts}
        self.meta[key] = new
        return new != old

    def discover(self) -> None:
        """Find the ha-bambulab entities of the printer, its AMS units and the external spool."""
        ent_reg, dev_reg = er.async_get(self.hass), dr.async_get(self.hass)
        printer_id = self.entry.data[CONF_PRINTER]
        for entity in er.async_entries_for_device(ent_reg, printer_id):
            if entity.platform == SOURCE_PLATFORM and entity.translation_key:
                self._printer[entity.translation_key] = entity.entity_id
        for entity in ent_reg.entities.values():
            if entity.platform != SOURCE_PLATFORM or entity.translation_key not in ("tray", "external_spool"):
                continue
            device = dev_reg.async_get(entity.device_id) if entity.device_id else None
            if device is None or device.via_device_id != printer_id:
                continue
            if entity.translation_key == "external_spool":
                self._slots[entity.entity_id] = "External Spool"
                continue
            # ha-bambulab names child devices '<printer>_AMS_1', '<printer>_AMS_HT_1'.
            ams = re.search(r"AMS_(HT_)?(\d+)$", device.name or "")
            tray = re.search(r"_tray_(\d+)$", entity.unique_id)
            if ams and ams.group(1):
                self._slots[entity.entity_id] = f"AMS HT {ams.group(2)}"
            elif tray:
                unit = ams.group(2) if ams else "1"
                self._slots[entity.entity_id] = f"AMS {unit} Tray {tray.group(1)}"
        missing = {"print_status", "print_weight", "print_progress"} - set(self._printer)
        if missing or not self._slots:
            raise ConfigEntryNotReady(f"ha-bambulab entities not found: {sorted(missing) or 'spool slots'}")

    def start(self) -> None:
        watched = [*self._printer.values(), *self._slots]
        self.entry.async_on_unload(async_track_state_change_event(self.hass, watched, self._changed))
        self.entry.async_on_unload(async_track_time_interval(self.hass, self.async_sync_profiles, SYNC_INTERVAL))
        self.refresh()

    @callback
    def _changed(self, _event: Event) -> None:
        self.refresh()

    @callback
    def refresh(self) -> None:
        """Read the printer state, register new items and deduct a finished job."""
        states = self.hass.states
        slots: dict[str, tuple[str | None, bool]] = {}
        seen: dict[str, dict] = {}
        for entity_id, slot in self._slots.items():
            if (state := states.get(entity_id)) is None:
                continue
            key, facts = slot_item(state.attributes, self.profiles) or (None, {})
            if key in self.aliases:
                # A merged profile: its grams are kept on the item it was merged into.
                slots[slot] = (self.aliases[key], bool(state.attributes.get("active")))
                continue
            if key:
                # Keep a profile name learnt earlier when the slot has none right now.
                seen[key] = {**{k: v for k, v in self.meta.get(key, {}).items() if k in ("profile", "brand")}, **facts}
            slots[slot] = (key, bool(state.attributes.get("active")))
        new = [key for key in seen if key not in self.items]
        renamed = False
        for key, facts in seen.items():
            changed = self._learn(key, facts)
            renamed |= changed and key in self.items
            self.items.setdefault(key, 0.0)
        if new:
            async_dispatcher_send(self.hass, self.signal_new, new)
        if new or renamed:
            self._save()
        if renamed:
            # Name and colour are part of the entities, reload to apply them.
            self.hass.config_entries.async_schedule_reload(self.entry.entry_id)

        status = states.get(self._printer["print_status"])
        progress = states.get(self._printer["print_progress"])
        weight = states.get(self._printer["print_weight"])
        weights = {}
        if weight is not None:
            weights = {
                k: float(v)
                for k, v in weight.attributes.items()
                if k.startswith(("AMS", "External")) and isinstance(v, (int, float))
            }
        usage = self.tracker.update(
            status.state if status else None,
            _number(progress.state) if progress else None,
            _number(weight.state) if weight else None,
            weights,
            slots,
        )
        if usage:
            factor = 1 + self.option(CONF_WASTE) / 100
            _LOGGER.info("Print ended, deducting %s (x%.2f waste)", usage, factor)
            for key, grams in usage.items():
                self.set(key, self.items.get(key, 0.0) - grams * factor)

    @callback
    def set(self, key: str, grams: float) -> None:
        old = self.items.get(key, 0.0)
        new = self.items[key] = round(max(0.0, grams), 1)
        self._save()
        async_dispatcher_send(self.hass, self.signal_update)
        low = self.option(CONF_LOW)
        if old >= low > new:
            title, text = LOW_MESSAGE.get(self.hass.config.language, LOW_MESSAGE["en"])
            persistent_notification.async_create(
                self.hass,
                text.format(item=self.label(key), grams=new, low=low),
                title,
                f"{DOMAIN}_{key}",
            )

    def label(self, key: str) -> str:
        return item_label(key, self.meta.get(key, {}), self.hass.config.language, self.brands)

    async def async_set_brands(self, brands: dict[str, str]) -> None:
        """Brand map (vendor -> shown brand); names are part of the entities, so the entry reloads."""
        self.brands = {k: v for k, v in brands.items() if k and v}
        await self._store.async_save(self._data())
        self.hass.config_entries.async_schedule_reload(self.entry.entry_id)

    async def async_merge(self, source: str, target: str) -> None:
        """Merge item source into target: grams and barcodes move, the source profile now counts as the target."""
        grams, codes = merge_plan(self.items, self.meta, source, target)
        self.items[target] = grams
        self.meta.setdefault(target, {})["barcodes"] = codes
        # Everything that pointed at the source follows it to the target.
        self.aliases = {k: (target if v == source else v) for k, v in self.aliases.items()}
        self.aliases[source] = target
        self.remove_item(source)
        await self._store.async_save(self._data())
        self.hass.config_entries.async_schedule_reload(self.entry.entry_id)

    async def async_rename_item(self, key: str, name: str) -> None:
        """Name typed by the user; empty goes back to the name from the printer."""
        meta = self.meta.setdefault(key, {})
        meta.pop("name", None)
        if name:
            meta["name"] = name
        # Saved right away: the caller reloads the entry, which reads the store again.
        await self._store.async_save(self._data())

    @callback
    def remove_item(self, key: str) -> None:
        self.items.pop(key, None)
        self.meta.pop(key, None)
        # Profiles merged into this item become items of their own again.
        self.aliases = {k: v for k, v in self.aliases.items() if v != key}
        self._save()
        ent_reg = er.async_get(self.hass)
        prefix = f"{self.entry.entry_id}_{key}_"
        for entity in er.async_entries_for_config_entry(ent_reg, self.entry.entry_id):
            if entity.unique_id.startswith(prefix):
                ent_reg.async_remove(entity.entity_id)

    @callback
    def add_spool(self, key: str) -> None:
        self.set(key, self.items.get(key, 0.0) + self.option(CONF_SPOOL))

    @callback
    def assign_barcode(self, key: str, code: str) -> None:
        """Remember that the barcode means this item (a code belongs to one item only)."""
        self.forget_barcode(code)
        self.meta.setdefault(key, {}).setdefault("barcodes", []).append(code)
        self._save()

    @callback
    def forget_barcode(self, code: str) -> None:
        for meta in self.meta.values():
            if code in meta.get("barcodes", ()):
                meta["barcodes"].remove(code)
        self._save()

    def _save(self) -> None:
        self._store.async_delay_save(self._data, 5)

    def _data(self) -> dict:
        return {"schema": SCHEMA, "items": self.items, "meta": self.meta, "brands": self.brands, "aliases": self.aliases}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    stock = Stock(hass, entry)
    stock.discover()
    await stock.async_load()
    await stock.async_load_profiles(cloud=True)
    entry.runtime_data = stock
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    stock.start()
    await async_setup_panel(hass)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
