"""Authentication models for Music Assistant API."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin


class UserRole(StrEnum):
    """User role enum."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class AuthProviderType(StrEnum):
    """Authentication provider type enum."""

    BUILTIN = "builtin"
    HOME_ASSISTANT = "homeassistant"


@dataclass
class User(DataClassORJSONMixin):
    """User model."""

    user_id: str
    username: str
    role: UserRole
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    display_name: str | None = None
    avatar_url: str | None = None
    preferences: dict[str, Any] = field(default_factory=dict)
    provider_filter: list[str] = field(default_factory=list)
    player_filter: list[str] = field(default_factory=list)


@dataclass
class UserAuthProvider(DataClassORJSONMixin):
    """Link between a User and an Authentication Provider."""

    link_id: str
    user_id: str
    provider_type: AuthProviderType
    provider_user_id: str  # The user ID from the provider (e.g., HA user ID)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AuthToken(DataClassORJSONMixin):
    """Authentication token model."""

    token_id: str
    user_id: str
    token_hash: str
    name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    is_long_lived: bool = False


@dataclass
class GuestAccessInfo(DataClassORJSONMixin):
    """Guest Access information dataclass."""

    enabled: bool
    guest_url: str | None
    guest_token: str | None
    can_play_media: bool
    can_control_queue: bool
    can_control_playback: bool
    can_control_volume: bool
    player_filter: list[str]
    provider_filter: list[str]
