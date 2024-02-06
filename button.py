"""Wyoming button entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.helpers import config_validation as cv

import voluptuous as vol

from .const import DOMAIN
from .entity import WyomingSatelliteEntity

if TYPE_CHECKING:
    from .models import DomainDataItem


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    item: DomainDataItem = hass.data[DOMAIN][config_entry.entry_id]

    # Setup is only forwarded for satellites
    assert item.satellite is not None

    device = item.satellite.device
    async_add_entities(
        [
            WyomingSatelliteDetectionButton(device),
            WyomingSatelliteAskButton(device),
        ]
    )

    platform = async_get_current_platform()
    # This will call Entity.set_sleep_timer(sleep_time=VALUE)
    platform.async_register_entity_service(
        "press_button",
        {
            vol.Required('question_id'): cv.string,
        },
        "async_handle_press_service",
    )        



class WyomingSatelliteDetectionButton(
    WyomingSatelliteEntity, ButtonEntity
):
    """Entity to trigger the STT (Detection event)."""

    entity_description = ButtonEntityDescription(
        key="detection",
        translation_key="detection",
    )

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

    async def async_press(self) -> None:
        """Press the button."""
        self._device.press_detection()

    async def async_handle_press_service(self, question_id: str) -> None:
        await self.async_press()

class WyomingSatelliteAskButton(
    WyomingSatelliteEntity, ButtonEntity
):
    """Entity to trigger the STT to get answer to a question (Detection event)."""

    entity_description = ButtonEntityDescription(
        key="ask",
        translation_key="ask",
    )

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

    async def async_press(self, question_id: Optional[str] = "ask") -> None:
        """Press the button."""
        self._device.press_ask(question_id)

    async def async_handle_press_service(self, question_id: str) -> None:
        await self.async_press(question_id)
