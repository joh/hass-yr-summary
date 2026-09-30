"""Set up the Yr Summary component (config entry / UI)."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_LANGUAGE, CONF_LOCATION_ID, CONF_SCAN_INTERVAL, DOMAIN
from .coordinator import YrAutotextCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config) -> bool:
    """Nothing to do at YAML level; everything is driven by config entries."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = YrAutotextCoordinator(
        hass,
        entry.data[CONF_LOCATION_ID],
        entry.data[CONF_LANGUAGE],
        entry.data.get(CONF_SCAN_INTERVAL),
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, (SENSOR_DOMAIN,))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, (SENSOR_DOMAIN,))
