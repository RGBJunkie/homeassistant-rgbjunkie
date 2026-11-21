"""Light entities: desk blob + per-device brightness."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RgbjunkieConfigEntry
from .const import DOMAIN
from .coordinator import RgbjunkieCoordinator

PARALLEL_UPDATES = 0


def _ha_brightness_to_percent(brightness: int) -> int:
    return max(0, min(100, round(int(brightness) * 100 / 255)))


def _percent_to_ha_brightness(percent: int) -> int:
    return max(1, min(255, round(int(percent) * 255 / 100)))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RgbjunkieConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    def _sync() -> None:
        nonlocal known
        entities: list[LightEntity] = []
        if "desk" not in known:
            known.add("desk")
            entities.append(DeskLight(coordinator, entry))
        for row in coordinator.devices:
            device_id = str(row.get("id") or "").strip()
            if not device_id or device_id in known:
                continue
            known.add(device_id)
            entities.append(DeviceLight(coordinator, entry, device_id))
        if entities:
            async_add_entities(entities)

    _sync()
    entry.async_on_unload(coordinator.async_add_listener(_sync))


class DeskLight(CoordinatorEntity[RgbjunkieCoordinator], LightEntity):
    """Whole-desk on/off + brightness."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self, coordinator: RgbjunkieCoordinator, entry: RgbjunkieConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._last_on_percent = 100
        self._attr_unique_id = f"{entry.entry_id}_desk_light"
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
        data = self.coordinator.data or {}
        lights_off = bool(data.get("lightsOff"))
        percent = int(data.get("brightnessPercent") or 0)
        if percent > 0:
            self._last_on_percent = percent
        self._attr_is_on = not lights_off
        self._attr_brightness = (
            _percent_to_ha_brightness(percent if percent > 0 else self._last_on_percent)
            if self._attr_is_on
            else None
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self.coordinator.pc_name,
            manufacturer="RGBJunkie",
            model="Lights3D Desk",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            percent = _ha_brightness_to_percent(int(kwargs[ATTR_BRIGHTNESS]))
            if percent <= 0:
                percent = self._last_on_percent or 100
            self._last_on_percent = percent
            await self.coordinator.api.set_brightness(percent)
        else:
            # Power toggle: restore the level from before off. Do not trust a
            # missing/stale HA brightness (that was the 5% bug).
            percent = self._last_on_percent or 100
            await self.coordinator.api.set_brightness(percent)
        await self.coordinator.api.set_lights(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        data = self.coordinator.data or {}
        percent = int(data.get("brightnessPercent") or 0)
        if percent > 0:
            self._last_on_percent = percent
        await self.coordinator.api.set_lights(False)
        await self.coordinator.async_request_refresh()


class DeviceLight(CoordinatorEntity[RgbjunkieCoordinator], LightEntity):
    """Per-controller brightness."""

    _attr_has_entity_name = True
    _attr_name = "Brightness"
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self,
        coordinator: RgbjunkieCoordinator,
        entry: RgbjunkieConfigEntry,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._device_id = device_id
        self._last_on_percent = 100
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_light"
        self._update_from_coordinator()

    def _row(self) -> dict[str, Any]:
        for row in self.coordinator.devices:
            if str(row.get("id") or "") == self._device_id:
                return row if isinstance(row, dict) else {}
        return {}

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_from_coordinator()
        super()._handle_coordinator_update()

    def _update_from_coordinator(self) -> None:
        row = self._row()
        name = str(row.get("name") or self._device_id)
        percent = int(row.get("brightnessPercent") or 0)
        if percent > 0:
            self._last_on_percent = percent
        self._attr_is_on = percent > 0
        self._attr_brightness = (
            _percent_to_ha_brightness(percent) if percent > 0 else None
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}:{self._device_id}")},
            name=name,
            manufacturer="RGBJunkie",
            model="Lights3D Device",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            percent = _ha_brightness_to_percent(int(kwargs[ATTR_BRIGHTNESS]))
            if percent <= 0:
                percent = self._last_on_percent or 100
        else:
            percent = self._last_on_percent or 100
        self._last_on_percent = percent
        await self.coordinator.api.set_device_brightness(self._device_id, percent)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        row = self._row()
        percent = int(row.get("brightnessPercent") or 0)
        if percent > 0:
            self._last_on_percent = percent
        await self.coordinator.api.set_device_brightness(self._device_id, 0)
        await self.coordinator.async_request_refresh()
