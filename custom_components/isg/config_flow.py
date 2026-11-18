"""Config flow for LinknLink iSG."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiohttp import ClientError, ClientTimeout

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = ClientTimeout(total=8)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


async def _validate(hass: HomeAssistant, host: str, port: int) -> None:
    if not host:
        raise CannotConnect
    session = async_get_clientsession(hass)
    url = f"http://{host}:{port}/api/v1/state"
    try:
        async with session.get(url, timeout=_TIMEOUT) as resp:
            if resp.status != 200:
                raise CannotConnect
            payload = await resp.json(content_type=None)
            if not isinstance(payload, dict) or "screen_on" not in payload:
                raise CannotConnect
    except CannotConnect:
        raise
    except (ClientError, TimeoutError, OSError, ValueError) as err:
        raise CannotConnect from err


class ISGConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LinknLink iSG."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            user_input[CONF_HOST] = host
            user_input[CONF_PORT] = port
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            try:
                await _validate(self.hass, host, port)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="LinknLink iSG", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
