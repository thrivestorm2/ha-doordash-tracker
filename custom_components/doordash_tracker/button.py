"""Buttons: stop tracking the current link, or poll the tracking page now."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DoorDashConfigEntry
from .entity import DoorDashEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: DoorDashConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities([DoorDashStopButton(coordinator), DoorDashRefreshButton(coordinator)])


class DoorDashStopButton(DoorDashEntity, ButtonEntity):
    """Clear the tracking link and return to idle right away."""

    _attr_name = "Stop tracking"
    _entity_domain = "button"
    _object_id = "stop_tracking"
    _attr_icon = "mdi:stop-circle-outline"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "stop")

    async def async_press(self) -> None:
        self.coordinator.async_stop()


class DoorDashRefreshButton(DoorDashEntity, ButtonEntity):
    """Poll the tracking page now instead of waiting for the next interval."""

    _attr_name = "Refresh now"
    _entity_domain = "button"
    _object_id = "refresh_now"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "refresh")

    async def async_press(self) -> None:
        await self.coordinator.async_refresh()
