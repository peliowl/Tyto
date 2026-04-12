"""Property definitions for TCard in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TCard


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TCard property definitions and factory."""

    CS = TCard.CardSize

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="title", label="Title", prop_type="str", default="Card",
            apply=lambda w, v: None,  # title is set at construction
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=CS.MEDIUM.value, options=_enum_options(CS),
            apply=lambda w, v: None,  # size is set at construction
        ),
        PropertyDefinition(
            name="hoverable", label="Hoverable", prop_type="bool", default=False,
            apply=lambda w, v: None,  # hoverable is set at construction
        ),
        PropertyDefinition(
            name="bordered", label="Bordered", prop_type="bool", default=True,
            apply=lambda w, v: None,  # bordered is set at construction
        ),
        PropertyDefinition(
            name="closable", label="Closable", prop_type="bool", default=False,
            apply=lambda w, v: None,  # closable is set at construction
        ),
    ]

    registry.register("card", definitions)
    registry.register_factory("card", lambda: TCard(title="Card"))
