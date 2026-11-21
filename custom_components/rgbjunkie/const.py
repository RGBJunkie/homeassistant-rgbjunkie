"""Constants for the RGBJunkie Lights3D Home Assistant integration."""

from homeassistant.const import Platform

DOMAIN = "rgbjunkie"
DEFAULT_PORT = 14224
DEFAULT_NAME = "RGBJunkie Desk"
USE_DESK_EFFECT = "Use desk effect"
CONF_TOKEN = "token"
SCAN_INTERVAL_SECONDS = 2

PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.SENSOR,
]
