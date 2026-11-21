"""RGBJunkie Lights3D Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RgbjunkieApi
from .const import CONF_TOKEN, DOMAIN
from .coordinator import RgbjunkieCoordinator

PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RGBJunkie from a config entry."""
    session = async_get_clientsession(hass)
    api = RgbjunkieApi(
        host=entry.data[CONF_HOST],
        port=int(entry.data[CONF_PORT]),
        token=entry.data[CONF_TOKEN],
        session=session,
    )
    coordinator = RgbjunkieCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
