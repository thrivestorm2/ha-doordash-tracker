"""Base entity for DoorDash Tracker."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DoorDashCoordinator


class DoorDashEntity(CoordinatorEntity[DoorDashCoordinator]):
    _attr_has_entity_name = True
    # Subclasses set these. Together they give the fixed entity ID
    # <domain>.doordash_tracker_<object_id>, which the README, the blueprint
    # defaults and the iOS shortcut rely on. Without it, Home Assistant can
    # prefix the ID with the device's area or a renamed device's name.
    _entity_domain: str
    _object_id: str

    def __init__(self, coordinator: DoorDashCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{key}"
        # Only used when the entity is first registered; existing entity IDs
        # (including ones the user renamed) are left alone.
        self.entity_id = f"{self._entity_domain}.doordash_tracker_{self._object_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="DoorDash Tracker",
            manufacturer="Community",
            entry_type=DeviceEntryType.SERVICE,
        )
