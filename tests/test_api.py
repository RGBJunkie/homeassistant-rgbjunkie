"""Unit tests for the Lights3D bridge HTTP client (no Home Assistant required)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

_API_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "rgbjunkie"
    / "api.py"
)


def _load_api_module():
    name = "rgbjunkie_api_under_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _API_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


api_mod = _load_api_module()
RgbjunkieApi = api_mod.RgbjunkieApi
RgbjunkieApiError = api_mod.RgbjunkieApiError
RgbjunkieAuthError = api_mod.RgbjunkieAuthError


class _FakeResponse:
    def __init__(self, status: int, payload: Any = None, text: str = "") -> None:
        self.status = status
        self._payload = payload
        self._text = text

    async def text(self) -> str:
        if self._text:
            return self._text
        if self._payload is None:
            return ""
        return "json"

    async def json(self, content_type: str | None = None) -> Any:
        return self._payload

    async def __aenter__(self) -> _FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None


@pytest.mark.asyncio
async def test_get_status_ok() -> None:
    session = MagicMock()
    session.request = MagicMock(
        return_value=_FakeResponse(
            200, {"pcName": "THE_BEAST", "brightnessPercent": 80}
        )
    )
    api = RgbjunkieApi("192.168.1.10", 14224, "secret", session)
    status = await api.get_status()
    assert status["pcName"] == "THE_BEAST"
    session.request.assert_called_once()
    args, kwargs = session.request.call_args
    assert args[0] == "GET"
    assert args[1].endswith("/ha/status")
    assert kwargs["headers"]["Authorization"] == "Bearer secret"


@pytest.mark.asyncio
async def test_auth_error() -> None:
    session = MagicMock()
    session.request = MagicMock(return_value=_FakeResponse(401, text="nope"))
    api = RgbjunkieApi("192.168.1.10", 14224, "bad", session)
    with pytest.raises(RgbjunkieAuthError):
        await api.get_status()


@pytest.mark.asyncio
async def test_http_error() -> None:
    session = MagicMock()
    session.request = MagicMock(return_value=_FakeResponse(500, text="boom"))
    api = RgbjunkieApi("192.168.1.10", 14224, "secret", session)
    with pytest.raises(RgbjunkieApiError):
        await api.set_brightness(50)


@pytest.mark.asyncio
async def test_catalog_helpers() -> None:
    session = MagicMock()
    session.request = MagicMock(
        side_effect=[
            _FakeResponse(200, {"effects": [{"id": "a", "name": "Waves"}]}),
            _FakeResponse(200, {"scenes": [{"name": "Night"}]}),
        ]
    )
    api = RgbjunkieApi("127.0.0.1", 14224, "t", session)
    effects = await api.get_effects()
    scenes = await api.get_scenes()
    assert effects[0]["name"] == "Waves"
    assert scenes[0]["name"] == "Night"
