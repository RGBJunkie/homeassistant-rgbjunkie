"""RGBJunkie Lights3D Home Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import RgbjunkieApi
from .const import CONF_TOKEN, DOMAIN, PLATFORMS
from .coordinator import RgbjunkieCoordinator

type RgbjunkieConfigEntry = ConfigEntry[RgbjunkieCoordinator]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the RGBJunkie integration (config entry only)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: RgbjunkieConfigEntry) -> bool:
    """Set up RGBJunkie from a config entry."""
    session = async_get_clientsession(hass)
    api = RgbjunkieApi(
        host=entry.data[CONF_HOST],
        port=int(entry.data[CONF_PORT]),
        token=entry.data[CONF_TOKEN],
        session=session,
    )
    coordinator = RgbjunkieCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RgbjunkieConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: RgbjunkieConfigEntry) -> None:
    """Reload when the config entry is updated (reauth / reconfigure)."""
    await hass.config_entries.async_reload(entry.entry_id)
