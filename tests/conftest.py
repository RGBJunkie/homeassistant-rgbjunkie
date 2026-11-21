"""Pytest fixtures for Home Assistant custom component tests."""

from __future__ import annotations

import pytest

try:
    import pytest_homeassistant_custom_component  # noqa: F401

    pytest_plugins = "pytest_homeassistant_custom_component"

    @pytest.fixture(autouse=True)
    def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
        """Enable loading custom_components/ in tests."""
        return None

except ImportError:
    pytest_plugins = ()
