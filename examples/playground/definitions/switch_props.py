"""Property definitions for TSwitch in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TSwitch


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TSwitch property definitions and factory."""

    SS = TSwitch.SwitchSize

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=SS.MEDIUM.value, options=_enum_options(SS),
            apply=lambda w, v: w.set_size(_to_enum(SS, v)),
        ),
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.setEnabled(not bool(v)),
        ),
        PropertyDefinition(
            name="loading", label="Loading", prop_type="bool", default=False,
            apply=lambda w, v: w.set_loading(bool(v)),
        ),
        PropertyDefinition(
            name="round", label="Round", prop_type="bool", default=True,
            apply=lambda w, v: w.set_round(bool(v)),
        ),
    ]

    registry.register("switch", definitions)
    registry.register_factory("switch", lambda: TSwitch())
