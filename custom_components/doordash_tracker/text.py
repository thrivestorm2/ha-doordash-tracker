"""Tracking URL text entity: paste a link here (or call text.set_value) to start."""
from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import DoorDashConfigEntry
from .entity import DoorDashEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: DoorDashConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([DoorDashUrlText(entry.runtime_data)])


class DoorDashUrlText(DoorDashEntity, TextEntity, RestoreEntity):
    _attr_name = "Tracking URL"
    _attr_icon = "mdi:link-variant"
    _attr_mode = TextMode.TEXT
    _attr_native_min = 0
    _attr_native_max = 255

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "url")

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) and last.state not in (
            None, "unknown", "unavailable", ""
        ):
            self.coordinator.set_url(last.state)
            await self.coordinator.async_request_refresh()

    @property
    def native_value(self) -> str:
        return self.coordinator.url_value

    async def async_set_value(self, value: str) -> None:
        self.coordinator.set_url(value.strip())
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        # Reflects auto-clear after delivery/timeout.
        self.async_write_ha_state()
