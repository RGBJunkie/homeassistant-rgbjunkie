"""Pytest fixtures for Home Assistant custom component tests."""

from __future__ import annotations

try:
    import pytest_homeassistant_custom_component  # noqa: F401

    pytest_plugins = "pytest_homeassistant_custom_component"
except ImportError:
    pytest_plugins = ()
