"""Config flow: pick the ha-bambulab printer; options hold waste, threshold and spool size."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr, entity_registry as er, selector

from .const import CONF_AI, CONF_LOW, CONF_PRINTER, CONF_SPOOL, CONF_WASTE, DEFAULTS, DOMAIN, SOURCE_PLATFORM


def _item_options(stock) -> list:
    """Stock items as select options: 'Generic PETG white (GFG99_FFFFFF)'."""
    return [selector.SelectOptionDict(value=key, label=f"{stock.label(key)} ({key})") for key in stock.items]


def _box(maximum: float, unit: str) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=0, max=maximum, step=1, unit_of_measurement=unit, mode=selector.NumberSelectorMode.BOX
        )
    )


class FilamentStockConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            device_id = user_input[CONF_PRINTER]
            entities = er.async_entries_for_device(er.async_get(self.hass), device_id)
            if any(e.platform == SOURCE_PLATFORM and e.translation_key == "print_weight" for e in entities):
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                device = dr.async_get(self.hass).async_get(device_id)
                name = (device.name_by_user or device.name) if device else device_id
                return self.async_create_entry(title=f"Filament {name}", data=user_input)
            errors["base"] = "not_printer"
        schema = vol.Schema(
            {
                vol.Required(CONF_PRINTER): selector.DeviceSelector(
                    selector.DeviceSelectorConfig(integration=SOURCE_PLATFORM)
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return FilamentStockOptionsFlow()


class FilamentStockOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        return self.async_show_menu(step_id="init", menu_options=["edit_item", "remove_item", "settings"])

    async def async_step_edit_item(self, user_input=None):
        stock = self.config_entry.runtime_data
        if user_input is not None:
            await stock.async_rename_item(user_input["item"], user_input.get("name", "").strip())
            # The name is part of the entity names, so reload to apply it.
            self.hass.config_entries.async_schedule_reload(self.config_entry.entry_id)
            return self.async_create_entry(data=dict(self.config_entry.options))
        options = _item_options(stock)
        schema = vol.Schema(
            {
                vol.Required("item"): selector.SelectSelector(selector.SelectSelectorConfig(options=options)),
                vol.Optional("name"): selector.TextSelector(),
            }
        )
        return self.async_show_form(step_id="edit_item", data_schema=schema)

    async def async_step_remove_item(self, user_input=None):
        stock = self.config_entry.runtime_data
        if user_input is not None:
            for key in user_input["items"]:
                stock.remove_item(key)
            return self.async_create_entry(data=dict(self.config_entry.options))
        options = _item_options(stock)
        schema = vol.Schema(
            {vol.Required("items"): selector.SelectSelector(selector.SelectSelectorConfig(options=options, multiple=True))}
        )
        return self.async_show_form(step_id="remove_item", data_schema=schema)

    async def async_step_settings(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = {**DEFAULTS, **self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(CONF_WASTE, default=current[CONF_WASTE]): _box(100, "%"),
                vol.Required(CONF_LOW, default=current[CONF_LOW]): _box(100000, "g"),
                vol.Required(CONF_SPOOL, default=current[CONF_SPOOL]): _box(100000, "g"),
                vol.Optional(CONF_AI, description={"suggested_value": current.get(CONF_AI)}): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="ai_task")
                ),
            }
        )
        return self.async_show_form(step_id="settings", data_schema=schema)
