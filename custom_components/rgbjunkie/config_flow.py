"""Config flow for RGBJunkie Lights3D."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RgbjunkieApi, RgbjunkieApiError, RgbjunkieAuthError
from .const import CONF_TOKEN, DEFAULT_NAME, DEFAULT_PORT, DOMAIN

STEP_USER = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_TOKEN): str,
    }
)


async def _validate(
    hass: HomeAssistant, host: str, port: int, token: str
) -> dict[str, str]:
    session = async_get_clientsession(hass)
    api = RgbjunkieApi(host=host, port=port, token=token, session=session)
    status = await api.get_status()
    name = str(status.get("pcName") or "").strip() or DEFAULT_NAME
    return {"title": name}


class RgbjunkieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    _reauth_entry: ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            token = user_input[CONF_TOKEN].strip()
            try:
                info = await _validate(self.hass, host, port, token)
            except RgbjunkieAuthError:
                errors["base"] = "invalid_auth"
            except (RgbjunkieApiError, aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_TOKEN: token,
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication when the token is rejected."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a fresh token (and optional host/port)."""
        errors: dict[str, str] = {}
        entry = self._reauth_entry
        if entry is None:
            return self.async_abort(reason="reauth_failed")

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                vol.Required(
                    CONF_PORT, default=int(entry.data[CONF_PORT])
                ): int,
                vol.Required(CONF_TOKEN): str,
            }
        )

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            token = user_input[CONF_TOKEN].strip()
            try:
                info = await _validate(self.hass, host, port, token)
            except RgbjunkieAuthError:
                errors["base"] = "invalid_auth"
            except (RgbjunkieApiError, aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_mismatch(reason="wrong_account")
                return self.async_update_reload_and_abort(
                    entry,
                    title=info["title"],
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_TOKEN: token,
                    },
                    reason="reauth_successful",
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user change host, port, or token."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                vol.Required(
                    CONF_PORT, default=int(entry.data[CONF_PORT])
                ): int,
                vol.Required(
                    CONF_TOKEN, default=entry.data[CONF_TOKEN]
                ): str,
            }
        )

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            token = user_input[CONF_TOKEN].strip()
            try:
                info = await _validate(self.hass, host, port, token)
            except RgbjunkieAuthError:
                errors["base"] = "invalid_auth"
            except (RgbjunkieApiError, aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_mismatch(reason="wrong_account")
                return self.async_update_reload_and_abort(
                    entry,
                    title=info["title"],
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_TOKEN: token,
                    },
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )
