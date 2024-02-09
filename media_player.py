"""Wyoming media_player entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)

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
    """Set up media_player entities."""
    item: DomainDataItem = hass.data[DOMAIN][config_entry.entry_id]

    # Setup is only forwarded for satellites
    assert item.satellite is not None

    device = item.satellite.device
    async_add_entities(
        [
            WyomingSatelliteMediaPlayer(device),
        ]
    )

    # Register service for remote trigger
    platform = async_get_current_platform()
    platform.async_register_entity_service(
        "remote_trigger",
        {
            vol.Optional("question_id"): cv.string,
        },
        "async_handle_remote_trigger",
    )


class WyomingSatelliteMediaPlayer(WyomingSatelliteEntity, MediaPlayerEntity):
    """Media Player Entity to support PLAY MEDIA for TTS."""

    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_supported_features = MediaPlayerEntityFeature.PLAY_MEDIA

    entity_description = MediaPlayerEntityDescription(
        key="speaker",
        translation_key="speaker",
    )

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()

    async def async_play_media(
        self, media_type: MediaType | str, media_id: str, **kwargs: Any
    ) -> None:
        self._device.play_media(media_id)

    @property
    def state(self) -> MediaPlayerState:
        """Return the media state."""
        return MediaPlayerState.ON

    async def async_handle_remote_trigger(self, question_id: Optional[str] = None) -> None:
        self._device.remote_trigger(question_id)
