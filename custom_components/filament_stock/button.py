"""Buttons: add one new spool to a stock item; read the profiles from Bambu again."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN
from .entity import ItemEntity, setup_items


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([SyncButton(entry)])
    setup_items(hass, entry, async_add_entities, AddSpoolButton)


class SyncButton(ButtonEntity):
    """Read the user's profiles from Bambu Cloud now instead of waiting for the next interval."""

    _attr_has_entity_name = True
    _attr_translation_key = "sync"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:cloud-sync"

    def __init__(self, entry) -> None:
        self.stock = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_sync"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name=entry.title, entry_type=DeviceEntryType.SERVICE
        )

    async def async_press(self) -> None:
        await self.stock.async_sync_profiles()


class AddSpoolButton(ItemEntity, ButtonEntity):
    _attr_translation_key = "add_spool"

    async def async_press(self) -> None:
        self.stock.add_spool(self.key)
