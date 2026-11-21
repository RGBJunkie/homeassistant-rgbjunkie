"""Paused switch for the desk blob."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
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
    async_add_entities([PausedSwitch(coordinator, entry)])


class PausedSwitch(CoordinatorEntity[RgbjunkieCoordinator], SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Paused"
    _attr_translation_key = "paused"

    def __init__(self, coordinator: RgbjunkieCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_paused"
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
        self._attr_is_on = bool((self.coordinator.data or {}).get("paused"))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api.set_paused(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api.set_paused(False)
        await self.coordinator.async_request_refresh()
