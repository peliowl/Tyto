"""Property definitions for TSpin in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TSpin


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TSpin property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=TSpin.SpinSize.MEDIUM.value, options=_enum_options(TSpin.SpinSize),
            apply=lambda w, v: w.set_size(_to_enum(TSpin.SpinSize, v)),
        ),
        PropertyDefinition(
            name="animation_type", label="Animation Type", prop_type="enum",
            default=TSpin.AnimationType.RING.value, options=_enum_options(TSpin.AnimationType),
            apply=lambda w, v: w.set_animation_type(_to_enum(TSpin.AnimationType, v)),
        ),
        PropertyDefinition(
            name="spinning", label="Spinning", prop_type="bool", default=True,
            apply=lambda w, v: w.set_spinning(bool(v)),
        ),
        PropertyDefinition(
            name="description", label="Description", prop_type="str", default="",
            apply=lambda w, v: w.set_description(str(v)),
        ),
        PropertyDefinition(
            name="stroke_width", label="Stroke Width", prop_type="int", default=2,
            apply=lambda w, v: w.set_stroke_width(int(v)) if int(v) > 0 else None,
        ),
        PropertyDefinition(
            name="stroke", label="Stroke Color", prop_type="color", default="",
            apply=lambda w, v: w.set_stroke(str(v) if v else None),
        ),
        PropertyDefinition(
            name="rotate", label="Rotate (custom icon)", prop_type="bool", default=True,
            apply=lambda w, v: w.set_rotate(bool(v)),
        ),
    ]

    registry.register("spin", definitions)
    registry.register_factory("spin", lambda: TSpin())
