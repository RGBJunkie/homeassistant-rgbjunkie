"""Diagnostics for RGBJunkie Lights3D."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from . import RgbjunkieConfigEntry
from .const import CONF_TOKEN

TO_REDACT = {CONF_TOKEN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: RgbjunkieConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    data = coordinator.data or {}
    devices = []
    for row in coordinator.devices:
        if not isinstance(row, dict):
            continue
        devices.append(
            {
                "id": row.get("id"),
                "name": row.get("name"),
                "brightnessPercent": row.get("brightnessPercent"),
                "usesDeskEffect": row.get("usesDeskEffect"),
                "effectName": row.get("effectName"),
            }
        )
    return {
        "entry": async_redact_data(
            {
                CONF_HOST: entry.data.get(CONF_HOST),
                CONF_PORT: entry.data.get(CONF_PORT),
                CONF_TOKEN: entry.data.get(CONF_TOKEN),
                "title": entry.title,
                "unique_id": entry.unique_id,
            },
            TO_REDACT,
        ),
        "status": {
            "pcName": data.get("pcName"),
            "lightsOff": data.get("lightsOff"),
            "brightnessPercent": data.get("brightnessPercent"),
            "paused": data.get("paused"),
            "sceneName": data.get("sceneName"),
            "effectName": data.get("effectName"),
            "devicesOnline": data.get("devicesOnline"),
            "devicesTotal": data.get("devicesTotal"),
            "effectFps": data.get("effectFps"),
        },
        "catalog": {
            "effects": len(coordinator.effects),
            "scenes": len(coordinator.scenes),
        },
        "devices": devices,
    }
