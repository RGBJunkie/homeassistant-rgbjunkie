"""Next/previous effect and scene buttons."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
    async_add_entities(
        [
            StepButton(coordinator, entry, "next_effect", "Next effect", False, True),
            StepButton(coordinator, entry, "previous_effect", "Previous effect", True, True),
            StepButton(coordinator, entry, "next_scene", "Next scene", False, False),
            StepButton(coordinator, entry, "previous_scene", "Previous scene", True, False),
        ]
    )


class StepButton(CoordinatorEntity[RgbjunkieCoordinator], ButtonEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RgbjunkieCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        previous: bool,
        effect: bool,
    ) -> None:
        super().__init__(coordinator)
        self._previous = previous
        self._effect = effect
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.pc_name,
            manufacturer="RGBJunkie",
            model="Lights3D Desk",
        )

    async def async_press(self) -> None:
        if self._effect:
            await self.coordinator.api.effect_step(self._previous)
        else:
            await self.coordinator.api.scene_step(self._previous)
        await self.coordinator.async_request_refresh()
