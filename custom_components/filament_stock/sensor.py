"""Grams on the spool in each AMS slot and the external spool."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfMass
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    stock = entry.runtime_data
    async_add_entities(SlotSensor(stock, slot) for slot in stock.slot_names)


class SlotSensor(SensorEntity):
    """Stock of the item in a slot, as the opened spool: the remainder after whole spools."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_translation_key = "slot"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_suggested_display_precision = 0
    _attr_icon = "mdi:printer-3d-nozzle"

    def __init__(self, stock, slot: str) -> None:
        self.stock = stock
        self.slot = slot
        entry_id = stock.entry.entry_id
        self._attr_unique_id = f"{entry_id}_slot_{slot.lower().replace(' ', '_')}"
        self._attr_translation_placeholders = {"slot": slot}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=stock.entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> float | None:
        return self.stock.loaded().get(self.slot)

    @property
    def extra_state_attributes(self) -> dict:
        key = self.stock.slot_items.get(self.slot)
        return {
            "item": key,
            "label": self.stock.label(key) if key else None,
            "stock": self.stock.items.get(key) if key else None,
        }

    async def async_added_to_hass(self) -> None:
        for signal in (self.stock.signal_update, self.stock.signal_slots):
            self.async_on_remove(async_dispatcher_connect(self.hass, signal, self.async_write_ha_state))
