
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_COOKIE,
    CONF_SCAN_INTERVAL_MIN,
    CONF_HISTORY_MONTHS,
    DEFAULT_SCAN_INTERVAL_MIN,
    DEFAULT_HISTORY_MONTHS,
)
from .api import EBlocAPI, EBlocAuthError


class EBlocConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            cookie = (user_input.get(CONF_COOKIE) or "").strip()
            scan_min = int(user_input.get(CONF_SCAN_INTERVAL_MIN, DEFAULT_SCAN_INTERVAL_MIN))
            hist = int(user_input.get(CONF_HISTORY_MONTHS, DEFAULT_HISTORY_MONTHS))

            try:
                api = EBlocAPI(async_get_clientsession(self.hass), cookie)
                await api.discover()
            except EBlocAuthError:
                errors["base"] = "auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"ebloc_ro_{api.id_asoc}_{api.id_ap or 'all'}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="e-Bloc Romania",
                    data={
                        CONF_COOKIE: cookie,
                        CONF_SCAN_INTERVAL_MIN: scan_min,
                        CONF_HISTORY_MONTHS: hist,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_COOKIE): str,
                vol.Optional(CONF_SCAN_INTERVAL_MIN, default=DEFAULT_SCAN_INTERVAL_MIN): int,
                vol.Optional(CONF_HISTORY_MONTHS, default=DEFAULT_HISTORY_MONTHS): vol.All(int, vol.Range(min=1, max=120)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)


class EBlocOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.entry.options or self.entry.data
        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL_MIN, default=data.get(CONF_SCAN_INTERVAL_MIN, DEFAULT_SCAN_INTERVAL_MIN)): int,
                vol.Optional(CONF_HISTORY_MONTHS, default=data.get(CONF_HISTORY_MONTHS, DEFAULT_HISTORY_MONTHS)): vol.All(int, vol.Range(min=1, max=120)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


async def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    return EBlocOptionsFlow(config_entry)
