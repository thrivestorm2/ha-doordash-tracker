"""Status sensor: state is "1"-"4" (step), "idle", or "error"."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DoorDashConfigEntry
from .entity import DoorDashEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: DoorDashConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([DoorDashStatusSensor(entry.runtime_data)])


class DoorDashStatusSensor(DoorDashEntity, SensorEntity):
    _attr_name = "Status"
    _entity_domain = "sensor"
    _object_id = "status"
    _attr_icon = "mdi:map-marker-path"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "status")

    @property
    def native_value(self) -> str:
        return (self.coordinator.data or {}).get("state", "idle")

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        return {
            "label": data.get("label", ""),
            "detail": data.get("detail", ""),
            "eta": data.get("eta", ""),
            "destination": data.get("destination", ""),
            "tracking": self.coordinator.url_code is not None,
        }
