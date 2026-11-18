"""Switch platform for LinknLink iSG."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ISGDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: ISGDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ISGScreenSwitch(coordinator, entry)])


class ISGScreenSwitch(CoordinatorEntity[ISGDataUpdateCoordinator], SwitchEntity):
    """Screen power switch."""

    _attr_has_entity_name = True
    _attr_translation_key = "screen"
    _attr_icon = "mdi:monitor"

    def __init__(
        self, coordinator: ISGDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_screen"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="LinknLink iSG",
            manufacturer="LinknLink",
            model="iSG",
        )

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return bool(self.coordinator.data.get("screen_on"))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_screen(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_screen(False)
