"""Data update coordinator for RGBJunkie Lights3D."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RgbjunkieApi, RgbjunkieApiError, RgbjunkieAuthError
from .const import DOMAIN, SCAN_INTERVAL_SECONDS


class RgbjunkieCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls Lights3D status and catalogs."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: RgbjunkieApi,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
            config_entry=entry,
        )
        self.api = api
        self.entry = entry
        self.effects: list[dict[str, Any]] = []
        self.scenes: list[dict[str, Any]] = []
        self._catalog_ticks = 0

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            status = await self.api.get_status()
            self._catalog_ticks += 1
            # Refresh often until both catalogs arrive, then every ~30 s.
            need_catalog = not self.effects or not self.scenes
            if need_catalog or self._catalog_ticks == 1 or self._catalog_ticks % 15 == 0:
                effects = await self.api.get_effects()
                scenes = await self.api.get_scenes()
                if effects:
                    self.effects = effects
                if scenes:
                    self.scenes = scenes
            return status
        except RgbjunkieAuthError as err:
            raise ConfigEntryAuthFailed("Invalid token") from err
        except RgbjunkieApiError as err:
            raise UpdateFailed(str(err)) from err

    @property
    def pc_name(self) -> str:
        data = self.data or {}
        name = str(data.get("pcName") or "").strip()
        return name or "RGBJunkie Desk"

    @property
    def devices(self) -> list[dict[str, Any]]:
        rows = (self.data or {}).get("devices")
        return rows if isinstance(rows, list) else []

    def effect_names(self) -> list[str]:
        return [
            str(e.get("name") or e.get("id") or "").strip()
            for e in self.effects
            if str(e.get("name") or e.get("id") or "").strip()
        ]

    def scene_names(self) -> list[str]:
        return [
            str(s.get("name") or "").strip()
            for s in self.scenes
            if str(s.get("name") or "").strip()
        ]
