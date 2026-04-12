"""Property definitions for TAlert in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TAlert


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TAlert property definitions and factory."""

    AT = TAlert.AlertType

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="alert_type", label="Type", prop_type="enum",
            default=AT.INFO.value, options=_enum_options(AT),
            apply=lambda w, v: w.set_alert_type(_to_enum(AT, v)),
        ),
        PropertyDefinition(
            name="title", label="Title", prop_type="str", default="Alert",
            apply=lambda w, v: w.set_title(str(v)),
        ),
        PropertyDefinition(
            name="description", label="Description", prop_type="str", default="This is an alert.",
            apply=lambda w, v: w.set_description(str(v)),
        ),
        PropertyDefinition(
            name="closable", label="Closable", prop_type="bool", default=False,
            apply=lambda w, v: w.set_closable(bool(v)),
        ),
        PropertyDefinition(
            name="bordered", label="Bordered", prop_type="bool", default=True,
            apply=lambda w, v: setattr(w, "bordered", bool(v)),
        ),
        PropertyDefinition(
            name="show_icon", label="Show Icon", prop_type="bool", default=True,
            apply=lambda w, v: setattr(w, "show_icon", bool(v)),
        ),
    ]

    registry.register("alert", definitions)
    registry.register_factory("alert", lambda: TAlert(title="Alert", description="This is an alert."))
