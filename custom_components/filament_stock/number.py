"""Grams left per stock item; editable to match reality."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfMass

from .const import CONF_SPOOL
from .entity import ItemEntity, setup_items


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    setup_items(hass, entry, async_add_entities, StockNumber)


class StockNumber(ItemEntity, NumberEntity):
    _attr_translation_key = "stock"
    _attr_device_class = NumberDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0
    _attr_native_max_value = 100000
    _attr_native_step = 1

    @property
    def native_value(self) -> float:
        return self.grams

    @property
    def extra_state_attributes(self) -> dict:
        meta = self.stock.meta.get(self.key, {})
        return {
            "profile": meta.get("profile"),
            "filament_id": self.key.partition("_")[0],
            "material": meta.get("material"),
            "brand": meta.get("brand"),
            "barcodes": meta.get("barcodes", []),
            "color": f"#{meta['color']}" if meta.get("color") else None,
            "spools": round(self.grams / self.stock.option(CONF_SPOOL), 2),
        }

    async def async_set_native_value(self, value: float) -> None:
        self.stock.set(self.key, value)
