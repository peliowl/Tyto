"""Property definitions for TEmpty in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TEmpty


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TEmpty property definitions and factory."""

    ES = TEmpty.EmptySize

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="description", label="Description", prop_type="str", default="\u6682\u65e0\u6570\u636e",
            apply=lambda w, v: w.set_description(str(v)),
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=ES.MEDIUM.value, options=_enum_options(ES),
            apply=lambda w, v: w.set_size(_to_enum(ES, v)),
        ),
        PropertyDefinition(
            name="show_icon", label="Show Icon", prop_type="bool", default=True,
            apply=lambda w, v: w.set_show_icon(bool(v)),
        ),
        PropertyDefinition(
            name="show_description", label="Show Description", prop_type="bool", default=True,
            apply=lambda w, v: w.set_show_description(bool(v)),
        ),
    ]

    registry.register("empty", definitions)
    registry.register_factory("empty", lambda: TEmpty())
