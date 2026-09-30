"""Coordinator that fetches the Yr daily text summary (autotext)."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_LANGUAGE,
    CONF_LOCATION_ID,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
)
from .yr_api import YrApiError, async_get_autotext

_LOGGER = logging.getLogger(__name__)


class YrAutotextCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches the Yr daily text summary for a location."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        location_id: str,
        language: str,
        scan_interval_minutes: int = DEFAULT_SCAN_INTERVAL_MINUTES,
        *,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN} {location_id} {language}",
            update_interval=timedelta(minutes=scan_interval_minutes),
        )
        self.location_id = location_id
        self.language = language

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        try:
            result = await async_get_autotext(session, self.location_id, self.language)
        except YrApiError as err:
            raise UpdateFailed(str(err)) from err

        try:
            updated = dt_util.parse_datetime(result["updated"])
            if updated is not None:
                result["updated_dt"] = updated.astimezone(dt_util.DEFAULT_TIME_ZONE)
        except (KeyError, TypeError, ValueError):
            pass
        return result
