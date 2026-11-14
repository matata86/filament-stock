"""Problem sensor: stock item below the low threshold."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .const import CONF_LOW
from .entity import ItemEntity, setup_items


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    setup_items(hass, entry, async_add_entities, LowSensor)


class LowSensor(ItemEntity, BinarySensorEntity):
    _attr_translation_key = "low"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        return self.grams < self.stock.option(CONF_LOW)
