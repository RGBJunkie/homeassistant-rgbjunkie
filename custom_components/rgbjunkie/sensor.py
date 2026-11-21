"""Diagnostic sensors on the desk blob."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RgbjunkieCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RgbjunkieCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DeskSensor(coordinator, entry, "devices_online", "Devices online", "devicesOnline"),
            DeskSensor(coordinator, entry, "devices_total", "Devices total", "devicesTotal"),
            DeskSensor(coordinator, entry, "effect_fps", "Effect FPS", "effectFps"),
        ]
    )


class DeskSensor(CoordinatorEntity[RgbjunkieCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: RgbjunkieCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        data_key: str,
    ) -> None:
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.pc_name,
            manufacturer="RGBJunkie",
            model="Lights3D Desk",
        )
        self._update_from_coordinator()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_from_coordinator()
        super()._handle_coordinator_update()

    def _update_from_coordinator(self) -> None:
        value = (self.coordinator.data or {}).get(self._data_key)
        self._attr_native_value = value
