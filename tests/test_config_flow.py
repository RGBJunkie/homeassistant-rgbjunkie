"""Config flow tests (requires pytest-homeassistant-custom-component)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.rgbjunkie.const import CONF_TOKEN, DOMAIN

pytestmark = pytest.mark.asyncio


async def test_user_flow_success(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    with patch(
        "custom_components.rgbjunkie.config_flow._validate",
        new=AsyncMock(return_value={"title": "THE_BEAST"}),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.68.85",
                CONF_PORT: 14224,
                CONF_TOKEN: "abc",
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "THE_BEAST"
    assert result["data"][CONF_HOST] == "192.168.68.85"
    assert result["data"][CONF_PORT] == 14224
    assert result["data"][CONF_TOKEN] == "abc"


async def test_user_flow_invalid_auth(hass: HomeAssistant) -> None:
    from custom_components.rgbjunkie.api import RgbjunkieAuthError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "custom_components.rgbjunkie.config_flow._validate",
        new=AsyncMock(side_effect=RgbjunkieAuthError("bad")),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.68.85",
                CONF_PORT: 14224,
                CONF_TOKEN: "bad",
            },
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"
