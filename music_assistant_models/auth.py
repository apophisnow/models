"""Authentication models for Music Assistant API."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Any

from mashumaro.mixins.orjson import DataClassORJSONMixin


class UserRole(StrEnum):
    """User role enum (legacy - only admin and user)."""

    ADMIN = "admin"
    USER = "user"


class PermissionScope(Enum):
    """Permission scopes for RBAC."""

    # Player permissions
    PLAYER_CONTROL = "player.control"  # Play, pause, stop, next, previous
    PLAYER_VOLUME = "player.volume"  # Adjust volume
    PLAYER_QUEUE = "player.queue"  # Add/remove from queue
    PLAYER_POWER = "player.power"  # Power on/off
    PLAYER_VIEW = "player.view"  # View player status

    # Library permissions
    LIBRARY_READ = "library.read"  # Browse and search library
    LIBRARY_WRITE = "library.write"  # Add/edit library items
    LIBRARY_DELETE = "library.delete"  # Delete library items

    # Playlist permissions
    PLAYLIST_READ = "playlist.read"  # View playlists
    PLAYLIST_WRITE = "playlist.write"  # Create/edit playlists
    PLAYLIST_DELETE = "playlist.delete"  # Delete playlists

    # Provider permissions
    PROVIDER_VIEW = "provider.view"  # View provider status
    PROVIDER_MANAGE = "provider.manage"  # Configure providers

    # System permissions
    SYSTEM_SETTINGS = "system.settings"  # Modify system settings
    SYSTEM_ADMIN = "system.admin"  # Full system administration

    # User permissions
    USER_READ = "user.read"  # View users
    USER_WRITE = "user.write"  # Create/edit users
    USER_DELETE = "user.delete"  # Delete users


class AuthProviderType(StrEnum):
    """Authentication provider type enum."""

    BUILTIN = "builtin"
    HOME_ASSISTANT = "homeassistant"


@dataclass
class User(DataClassORJSONMixin):
    """User model."""

    user_id: str
    username: str
    role: str  # RBAC role_id (e.g., "admin", "user", "guest", "dj", or custom role)
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
class Permission(DataClassORJSONMixin):
    """Represents a single permission."""

    permission_id: str
    scope: PermissionScope
    name: str
    description: str
    created_at: datetime


@dataclass
class Role(DataClassORJSONMixin):
    """Represents a user role with permissions."""

    role_id: str
    name: str
    description: str
    is_system: bool  # System roles cannot be deleted
    permissions: list[PermissionScope] = field(default_factory=list)
    created_at: datetime | None = None

    def has_permission(self, permission: PermissionScope | str) -> bool:
        """
        Check if role has a specific permission.

        :param permission: Permission to check.
        :return: True if role has permission.
        """
        if isinstance(permission, str):
            try:
                permission = PermissionScope(permission)
            except ValueError:
                return False

        # System admin has all permissions
        if PermissionScope.SYSTEM_ADMIN in self.permissions:
            return True

        return permission in self.permissions


# Default system roles
DEFAULT_ROLES = {
    "admin": Role(
        role_id="admin",
        name="Administrator",
        description="Full system access with all permissions",
        is_system=True,
        permissions=[PermissionScope.SYSTEM_ADMIN],
    ),
    "user": Role(
        role_id="user",
        name="Standard User",
        description="Standard user with basic playback and library access",
        is_system=True,
        permissions=[
            PermissionScope.PLAYER_CONTROL,
            PermissionScope.PLAYER_VOLUME,
            PermissionScope.PLAYER_QUEUE,
            PermissionScope.PLAYER_VIEW,
            PermissionScope.LIBRARY_READ,
            PermissionScope.PLAYLIST_READ,
            PermissionScope.PLAYLIST_WRITE,
            PermissionScope.PROVIDER_VIEW,
        ],
    ),
    "guest": Role(
        role_id="guest",
        name="Guest",
        description="Limited read-only access",
        is_system=True,
        permissions=[
            PermissionScope.PLAYER_VIEW,
            PermissionScope.LIBRARY_READ,
            PermissionScope.PLAYLIST_READ,
        ],
    ),
    "dj": Role(
        role_id="dj",
        name="DJ",
        description="Playback control and queue management without library modifications",
        is_system=True,
        permissions=[
            PermissionScope.PLAYER_CONTROL,
            PermissionScope.PLAYER_VOLUME,
            PermissionScope.PLAYER_QUEUE,
            PermissionScope.PLAYER_VIEW,
            PermissionScope.LIBRARY_READ,
            PermissionScope.PLAYLIST_READ,
        ],
    ),
}
