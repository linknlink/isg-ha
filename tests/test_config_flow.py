"""Tests for the LinknLink iSG config flow, including unattended defaults."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
import voluptuous as vol

from custom_components.isg.config_flow import (
    CannotConnect,
    ISGConfigFlow,
    STEP_USER_DATA_SCHEMA,
    _validate,
    normalized_user_input,
)
from custom_components.isg.const import CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT  # noqa: E402


def test_schema_empty_submit_uses_defaults() -> None:
    data = STEP_USER_DATA_SCHEMA({})
    assert data[CONF_HOST] == DEFAULT_HOST
    assert data[CONF_PORT] == DEFAULT_PORT


def test_schema_optional_not_required() -> None:
    # vol.Required would still be marked required in HA's data_schema and
    # would cause isgservicemanager CreateEntry to abort as needing input.
    for key in STEP_USER_DATA_SCHEMA.schema:
        assert isinstance(key, vol.Optional)


def test_normalized_empty_and_whitespace_host() -> None:
    assert normalized_user_input({}) == {CONF_HOST: DEFAULT_HOST, CONF_PORT: DEFAULT_PORT}
    assert normalized_user_input({CONF_HOST: "  ", CONF_PORT: DEFAULT_PORT})[CONF_HOST] == DEFAULT_HOST
    custom = normalized_user_input({CONF_HOST: " 10.0.0.8 ", CONF_PORT: "18951"})
    assert custom == {CONF_HOST: "10.0.0.8", CONF_PORT: 18951}


def test_schema_rejects_invalid_port() -> None:
    with pytest.raises(vol.Invalid):
        STEP_USER_DATA_SCHEMA({CONF_PORT: 0})
    with pytest.raises(vol.Invalid):
        STEP_USER_DATA_SCHEMA({CONF_PORT: 70000})


class _Resp:
    def __init__(self, status: int, payload: Any) -> None:
        self.status = status
        self._payload = payload

    async def json(self, content_type: Any = None) -> Any:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    async def __aenter__(self) -> _Resp:
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


class _Session:
    def __init__(self, status: int = 200, payload: Any = None, error: Exception | None = None) -> None:
        self.status = status
        self.payload = {"screen_on": True} if payload is None else payload
        self.error = error
        self.urls: list[str] = []

    def get(self, url: str, timeout: Any = None) -> Any:
        self.urls.append(url)
        if self.error:
            raise self.error
        return _Resp(self.status, self.payload)


@pytest.mark.asyncio
async def test_validate_ok() -> None:
    hass = MagicMock()
    session = _Session()
    hass.session = session
    await _validate(hass, DEFAULT_HOST, DEFAULT_PORT)
    assert session.urls == [f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/api/v1/state"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    [
        {"status": 500},
        {"payload": {"volume": 1}},
        {"payload": "not-a-dict"},
        {"error": TimeoutError("timeout")},
    ],
)
async def test_validate_cannot_connect(kwargs: dict[str, Any]) -> None:
    hass = MagicMock()
    hass.session = _Session(**kwargs)
    with pytest.raises(CannotConnect):
        await _validate(hass, DEFAULT_HOST, DEFAULT_PORT)


@pytest.mark.asyncio
async def test_user_step_shows_form_without_input() -> None:
    flow = ISGConfigFlow()
    result = await flow.async_step_user(None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_empty_submit_succeeds_when_reachable() -> None:
    flow = ISGConfigFlow()
    flow.hass.session = _Session()
    result = await flow.async_step_user({})
    assert result["type"] == "create_entry"
    assert result["title"] == "LinknLink iSG"
    assert result["data"] == {CONF_HOST: DEFAULT_HOST, CONF_PORT: DEFAULT_PORT}
    assert flow.unique_id == f"{DEFAULT_HOST}:{DEFAULT_PORT}"


@pytest.mark.asyncio
async def test_empty_submit_fails_when_unreachable() -> None:
    flow = ISGConfigFlow()
    flow.hass.session = _Session(status=503)
    result = await flow.async_step_user({})
    assert result["type"] == "form"
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_manual_custom_host_port() -> None:
    flow = ISGConfigFlow()
    flow.hass.session = _Session()
    result = await flow.async_step_user({CONF_HOST: "192.168.1.10", CONF_PORT: 18952})
    assert result["type"] == "create_entry"
    assert result["data"] == {CONF_HOST: "192.168.1.10", CONF_PORT: 18952}
    assert flow.unique_id == "192.168.1.10:18952"
