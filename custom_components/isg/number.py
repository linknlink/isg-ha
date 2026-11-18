"""Number platform for LinknLink iSG."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
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
    async_add_entities(
        [
            ISGVolumeNumber(coordinator, entry),
            ISGBrightnessNumber(coordinator, entry),
        ]
    )


class _ISGNumber(CoordinatorEntity[ISGDataUpdateCoordinator], NumberEntity):
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: ISGDataUpdateCoordinator, entry: ConfigEntry, key: str
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="LinknLink iSG",
            manufacturer="LinknLink",
            model="iSG",
        )


class ISGVolumeNumber(_ISGNumber):
    """Media volume as 0-100 percent."""

    _attr_translation_key = "volume"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self, coordinator: ISGDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "volume")

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        volume = self.coordinator.data.get("volume") or {}
        percent = volume.get("percent")
        return None if percent is None else float(percent)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_volume_percent(int(round(value)))


class ISGBrightnessNumber(_ISGNumber):
    """Display brightness 0-255."""

    _attr_translation_key = "brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, coordinator: ISGDataUpdateCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "brightness")

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get("brightness") is not None
        )

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get("brightness")
        return None if value is None else float(value)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_brightness(int(round(value)))
