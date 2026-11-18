"""Data update coordinator for LinknLink iSG."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = ClientTimeout(total=8)


class ISGApiError(HomeAssistantError):
    """Error talking to isgandroidcontrol."""


class ISGDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll isgandroidcontrol on localhost."""

    def __init__(
        self, hass: HomeAssistant, session: ClientSession, host: str, port: int
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._session = session
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.async_request("GET", "/api/v1/state")
        except ISGApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_request(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Call the local isgandroidcontrol API."""
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(
                method, url, json=json, timeout=_TIMEOUT
            ) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except ValueError as err:
                    raise ISGApiError(
                        f"{method} {path} returned invalid JSON: {err}"
                    ) from err
                if resp.status >= 400:
                    message = (
                        payload.get("error") if isinstance(payload, dict) else resp.reason
                    )
                    raise ISGApiError(f"{method} {path} failed: {message}")
                if not isinstance(payload, dict):
                    raise ISGApiError(f"{method} {path} returned unexpected payload")
                return payload
        except ISGApiError:
            raise
        except (ClientError, TimeoutError, OSError) as err:
            raise ISGApiError(
                f"Cannot reach isgandroidcontrol at {url}: {err}"
            ) from err

    async def async_set_screen(self, on: bool) -> None:
        data = await self.async_request(
            "POST", "/api/v1/screen", {"state": "on" if on else "off"}
        )
        self.async_set_updated_data(data)

    async def async_set_volume_percent(self, percent: int) -> None:
        data = await self.async_request(
            "POST", "/api/v1/volume", {"percent": int(percent)}
        )
        self.async_set_updated_data(data)

    async def async_set_brightness(self, value: int) -> None:
        data = await self.async_request(
            "POST", "/api/v1/brightness", {"value": int(value)}
        )
        self.async_set_updated_data(data)
