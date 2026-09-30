"""Config flow for the Yr Summary component."""
from __future__ import annotations

import re

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_LANGUAGE,
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    LANGUAGES,
)
from .yr_api import (
    Location,
    YrApiError,
    async_get_location,
    async_suggest_locations,
)

# Yr location ids look like '1-211102' (category-code + GeoNames id).
LOCATION_ID_RE = re.compile(r"^\d+-\d+$")


async def _resolve_location(
    session, user_input: str
) -> tuple[Location | None, list[Location]]:
    """Resolve user input to a Location, or a list of candidates."""
    user_input = user_input.strip()
    if LOCATION_ID_RE.match(user_input):
        location = await async_get_location(session, user_input)
        return location, []
    candidates = await async_suggest_locations(session, user_input)
    if len(candidates) == 1:
        return candidates[0], []
    return None, candidates


class YrSummaryConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yr Summary."""

    VERSION = 1

    _candidates: list[Location] = []
    _language: str = DEFAULT_LANGUAGE

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                location, candidates = await _resolve_location(
                    session, user_input["location"]
                )
            except YrApiError:
                errors["location"] = "cannot_connect"
            else:
                if location is None:
                    if not candidates:
                        errors["location"] = "no_results"
                    else:
                        self._candidates = candidates
                        self._language = user_input[CONF_LANGUAGE]
                        return await self.async_step_select_location()
                else:
                    await self.async_set_unique_id(
                        f"{location.location_id}_{user_input[CONF_LANGUAGE]}"
                    )
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=location.display_name,
                        data={
                            CONF_LOCATION_ID: location.location_id,
                            CONF_LOCATION_NAME: location.display_name,
                            CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL_MINUTES,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("location"): str,
                    vol.Required(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(
                        LANGUAGES
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_select_location(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            location = next(
                c for c in self._candidates if c.location_id == user_input["choice"]
            )
            language = self._language
            await self.async_set_unique_id(f"{location.location_id}_{language}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=location.display_name,
                data={
                    CONF_LOCATION_ID: location.location_id,
                    CONF_LOCATION_NAME: location.display_name,
                    CONF_LANGUAGE: language,
                    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL_MINUTES,
                },
            )

        return self.async_show_form(
            step_id="select_location",
            data_schema=vol.Schema(
                {
                    vol.Required("choice"): vol.In(
                        {c.location_id: c.display_name for c in self._candidates}
                    )
                }
            ),
        )
