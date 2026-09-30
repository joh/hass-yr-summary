"""Sensor that exposes the Yr daily text summary as its state."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_LANGUAGE,
    CONF_LOCATION_NAME,
    DOMAIN,
)
from .coordinator import YrAutotextCoordinator


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    coordinator: YrAutotextCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([YrSummarySensor(coordinator, entry.data)])


class YrSummarySensor(CoordinatorEntity[YrAutotextCoordinator], SensorEntity):
    """State is the official Yr daily text summary for a location."""

    _attr_name = "Yr summary"
    _attr_icon = "mdi:text-box-check"

    def __init__(self, coordinator: YrAutotextCoordinator, entry_data: dict) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"yr_summary_{coordinator.location_id}_{coordinator.language}"
        )
        self._location_name = entry_data[CONF_LOCATION_NAME]
        self._language = entry_data[CONF_LANGUAGE]

    @property
    def state(self) -> str | None:
        data = self.coordinator.data
        if not data:
            return None
        return data.get("text")

    @property
    def extra_state_attributes(self) -> dict:
        attrs: dict = {
            "location": self._location_name,
            "language": self._language,
        }
        data = self.coordinator.data or {}
        if updated := data.get("updated_dt"):
            attrs["updated"] = updated.isoformat()
        return attrs
