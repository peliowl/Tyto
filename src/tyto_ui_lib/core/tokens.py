"""Design Token data model and file loader.

Provides the DesignTokenSet dataclass for representing a complete set of
semantic design tokens, and utilities for loading/validating token definitions
from JSON files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class TokenFileError(Exception):
    """Raised when a design token file is malformed or invalid.

    Attributes:
        message: Human-readable description of the error.
        location: Optional location hint (e.g. missing key name, line number).
    """

    def __init__(self, message: str, location: str = "") -> None:
        self.location = location
        full = f"{message} (at: {location})" if location else message
        super().__init__(full)


# -- Required keys per token category --

REQUIRED_COLOR_KEYS: frozenset[str] = frozenset(
    {
        "primary",
        "primary_hover",
        "primary_pressed",
        "success",
        "warning",
        "error",
        "info",
        "bg_default",
        "bg_elevated",
        "text_primary",
        "text_secondary",
        "text_disabled",
        "border",
        "border_focus",
        "white",
        "mask",
    }
)

REQUIRED_SPACING_KEYS: frozenset[str] = frozenset({"small", "medium", "large", "xlarge"})
REQUIRED_RADIUS_KEYS: frozenset[str] = frozenset({"small", "medium", "large"})
REQUIRED_FONT_SIZE_KEYS: frozenset[str] = frozenset({"small", "medium", "large", "xlarge"})
REQUIRED_SHADOW_KEYS: frozenset[str] = frozenset({"small", "medium", "large"})


@dataclass
class DesignTokenSet:
    """A complete set of design tokens for one theme.

    Each field maps semantic names to their concrete values.
    All required keys must be present after loading from file.

    Attributes:
        name: Theme identifier (e.g. "light", "dark").
        colors: Semantic color tokens mapping name to CSS color string.
        spacing: Spacing tokens mapping name to pixel value.
        radius: Border-radius tokens mapping name to pixel value.
        font_sizes: Font-size tokens mapping name to pixel value.
        shadows: Box-shadow tokens mapping name to CSS shadow string.
    """

    name: str = ""
    colors: dict[str, str] = field(default_factory=dict)
    spacing: dict[str, int] = field(default_factory=dict)
    radius: dict[str, int] = field(default_factory=dict)
    font_sizes: dict[str, int] = field(default_factory=dict)
    shadows: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the token set to a plain dictionary (JSON-compatible)."""
        return {
            "name": self.name,
            "colors": dict(self.colors),
            "spacing": dict(self.spacing),
            "radius": dict(self.radius),
            "font_sizes": dict(self.font_sizes),
            "shadows": dict(self.shadows),
        }


# -- Validation helpers --

_CATEGORY_SPEC: dict[str, tuple[str, frozenset[str], type]] = {
    "colors": ("colors", REQUIRED_COLOR_KEYS, str),
    "spacing": ("spacing", REQUIRED_SPACING_KEYS, int),
    "radius": ("radius", REQUIRED_RADIUS_KEYS, int),
    "font_sizes": ("font_sizes", REQUIRED_FONT_SIZE_KEYS, int),
    "shadows": ("shadows", REQUIRED_SHADOW_KEYS, str),
}


def _validate_raw(data: dict[str, Any]) -> None:
    """Validate raw parsed JSON data against the token schema.

    Raises:
        TokenFileError: If any required category or key is missing, or if
            a value has an unexpected type.
    """
    for category, (_, required_keys, expected_type) in _CATEGORY_SPEC.items():
        if category not in data:
            raise TokenFileError(f"Missing required category '{category}'", location=category)

        section = data[category]
        if not isinstance(section, dict):
            raise TokenFileError(
                f"Category '{category}' must be an object, got {type(section).__name__}",
                location=category,
            )

        missing = required_keys - section.keys()
        if missing:
            raise TokenFileError(
                f"Missing required keys in '{category}': {sorted(missing)}",
                location=category,
            )

        for key, value in section.items():
            if not isinstance(value, expected_type):
                raise TokenFileError(
                    f"Key '{category}.{key}' expected {expected_type.__name__}, "
                    f"got {type(value).__name__}",
                    location=f"{category}.{key}",
                )


def _parse_token_set(data: dict[str, Any]) -> DesignTokenSet:
    """Build a DesignTokenSet from validated raw data."""
    return DesignTokenSet(
        name=data.get("name", ""),
        colors=data["colors"],
        spacing=data["spacing"],
        radius=data["radius"],
        font_sizes=data["font_sizes"],
        shadows=data["shadows"],
    )


def load_tokens_from_file(path: str | Path) -> DesignTokenSet:
    """Load and validate design tokens from a JSON file.

    Args:
        path: Filesystem path to the JSON token file.

    Returns:
        A validated DesignTokenSet instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        TokenFileError: If the JSON is malformed or fails validation.

    Example:
        >>> tokens = load_tokens_from_file("styles/tokens/light.json")
        >>> tokens.colors["primary"]
        '#18a058'
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Token file not found: {filepath}")

    raw_text = filepath.read_text(encoding="utf-8")

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise TokenFileError(
            f"Invalid JSON syntax: {exc.msg}",
            location=f"line {exc.lineno}, column {exc.colno}",
        ) from exc

    if not isinstance(data, dict):
        raise TokenFileError("Token file root must be a JSON object")

    _validate_raw(data)
    return _parse_token_set(data)
