"""HTTP client for the Lights3D Home Assistant bridge."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp


class RgbjunkieApiError(Exception):
    """Bridge request failed."""


class RgbjunkieAuthError(RgbjunkieApiError):
    """Token rejected."""


class RgbjunkieApi:
    """Talks to Lights3D on the LAN HA bridge port."""

    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._base = f"http://{host}:{port}"
        self._token = token.strip()
        self._session = session

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self._base}{path}"
        try:
            async with self._session.request(
                method,
                url,
                json=body,
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                text = await resp.text()
                if resp.status == 401:
                    raise RgbjunkieAuthError("unauthorized")
                if resp.status >= 400:
                    raise RgbjunkieApiError(f"HTTP {resp.status}: {text[:200]}")
                if not text:
                    return {}
                try:
                    return await resp.json(content_type=None)
                except Exception:
                    return {}
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise RgbjunkieApiError(str(err)) from err

    async def get_status(self) -> dict[str, Any]:
        data = await self._request("GET", "/ha/status")
        return data if isinstance(data, dict) else {}

    async def get_effects(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/ha/catalog/effects")
        rows = data.get("effects") if isinstance(data, dict) else None
        return rows if isinstance(rows, list) else []

    async def get_scenes(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/ha/catalog/scenes")
        rows = data.get("scenes") if isinstance(data, dict) else None
        return rows if isinstance(rows, list) else []

    async def set_lights(self, on: bool) -> None:
        await self._request("POST", "/ha/lights", {"on": on})

    async def set_brightness(self, percent: int) -> None:
        await self._request("POST", "/ha/brightness", {"percent": int(percent)})

    async def set_scene(self, name: str) -> None:
        await self._request("POST", "/ha/scene", {"name": name})

    async def set_effect(self, name: str) -> None:
        await self._request("POST", "/ha/effect", {"name": name})

    async def set_paused(self, paused: bool) -> None:
        await self._request("POST", "/ha/pause", {"paused": paused})

    async def effect_step(self, previous: bool) -> None:
        await self._request("POST", "/ha/effect/step", {"previous": previous})

    async def scene_step(self, previous: bool) -> None:
        await self._request("POST", "/ha/scene/step", {"previous": previous})

    async def set_device_effect(self, device_id: str, effect_id: str) -> None:
        await self._request(
            "POST",
            "/ha/device/effect",
            {"deviceId": device_id, "effectId": effect_id},
        )

    async def clear_device_effect(self, device_id: str) -> None:
        await self._request("POST", "/ha/device/effect/clear", {"deviceId": device_id})

    async def set_device_brightness(self, device_id: str, percent: int) -> None:
        await self._request(
            "POST",
            "/ha/device/brightness",
            {"deviceId": device_id, "percent": int(percent)},
        )
