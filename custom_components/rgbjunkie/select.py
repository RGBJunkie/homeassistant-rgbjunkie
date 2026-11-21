"""Scene / effect selects for desk and devices."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, USE_DESK_EFFECT
from .coordinator import RgbjunkieCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RgbjunkieCoordinator = hass.data[DOMAIN][entry.entry_id]
    known: set[str] = set()

    def _sync() -> None:
        nonlocal known
        entities: list[SelectEntity] = []
        for key, cls in (
            ("desk_scene", DeskSceneSelect),
            ("desk_effect", DeskEffectSelect),
        ):
            if key not in known:
                known.add(key)
                entities.append(cls(coordinator, entry))
        for row in coordinator.devices:
            device_id = str(row.get("id") or "").strip()
            key = f"dev_{device_id}"
            if not device_id or key in known:
                continue
            known.add(key)
            entities.append(DeviceEffectSelect(coordinator, entry, device_id))
        if entities:
            async_add_entities(entities)

    _sync()
    entry.async_on_unload(coordinator.async_add_listener(_sync))


class DeskSceneSelect(CoordinatorEntity[RgbjunkieCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Scene"
    _attr_translation_key = "scene"

    def __init__(self, coordinator: RgbjunkieCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_scene"
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
        options = self.coordinator.scene_names()
        current = str((self.coordinator.data or {}).get("sceneName") or "").strip()
        if current and current not in options:
            options = [current, *options]
        self._attr_options = options
        self._attr_current_option = current if current in options else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.set_scene(option)
        await self.coordinator.async_request_refresh()


class DeskEffectSelect(CoordinatorEntity[RgbjunkieCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Effect"
    _attr_translation_key = "effect"

    def __init__(self, coordinator: RgbjunkieCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_effect"
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
        options = self.coordinator.effect_names()
        current = str((self.coordinator.data or {}).get("effectName") or "").strip()
        if current and current not in options:
            options = [current, *options]
        self._attr_options = options
        self._attr_current_option = current if current in options else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.set_effect(option)
        await self.coordinator.async_request_refresh()


class DeviceEffectSelect(CoordinatorEntity[RgbjunkieCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Effect"
    _attr_translation_key = "device_effect"

    def __init__(
        self,
        coordinator: RgbjunkieCoordinator,
        entry: ConfigEntry,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._device_id = device_id
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_effect"
        self._update_from_coordinator()

    def _row(self) -> dict:
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
        options = [USE_DESK_EFFECT, *self.coordinator.effect_names()]
        if bool(row.get("usesDeskEffect")):
            current = USE_DESK_EFFECT
        else:
            current = str(row.get("effectName") or "").strip() or USE_DESK_EFFECT
        if current and current not in options:
            options = [current, *options]
        self._attr_options = options
        self._attr_current_option = current if current in options else USE_DESK_EFFECT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.entry_id}:{self._device_id}")},
            name=name,
            manufacturer="RGBJunkie",
            model="Lights3D Device",
            via_device=(DOMAIN, self._entry.entry_id),
        )

    async def async_select_option(self, option: str) -> None:
        if option == USE_DESK_EFFECT:
            await self.coordinator.api.clear_device_effect(self._device_id)
        else:
            # Prefer catalog id when we can match the display name.
            effect_id = option
            for row in self.coordinator.effects:
                if str(row.get("name") or "") == option:
                    effect_id = str(row.get("id") or option)
                    break
            await self.coordinator.api.set_device_effect(self._device_id, effect_id)
        await self.coordinator.async_request_refresh()
