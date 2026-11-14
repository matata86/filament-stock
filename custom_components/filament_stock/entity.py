"""Shared base for the per-item entities."""

from __future__ import annotations

from urllib.parse import quote

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class ItemEntity(Entity):
    """One entity of one stock item (a slicer profile, built-in ones per colour)."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, stock, key: str) -> None:
        self.stock = stock
        self.key = key
        entry_id = stock.entry.entry_id
        self._attr_unique_id = f"{entry_id}_{key}_{self._attr_translation_key}"
        self._attr_translation_placeholders = {"item": stock.label(key)}
        # Colour swatch shown in place of the icon.
        if color := stock.meta.get(key, {}).get("color"):
            self._attr_entity_picture = "data:image/svg+xml," + quote(
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><circle cx='12' cy='12' r='10' "
                f"fill='#{color}' stroke='#888' stroke-width='1.5'/></svg>"
            )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=stock.entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def grams(self) -> float:
        return self.stock.items.get(self.key, 0.0)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self.stock.signal_update, self.async_write_ha_state)
        )


def setup_items(hass, entry, async_add_entities, cls) -> None:
    """Add one entity per stock item, now and whenever a new item appears."""
    stock = entry.runtime_data

    @callback
    def _add(keys) -> None:
        async_add_entities(cls(stock, key) for key in keys)

    _add(list(stock.items))
    entry.async_on_unload(async_dispatcher_connect(hass, stock.signal_new, _add))
