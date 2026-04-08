"""Property definitions for TCheckbox in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TCheckbox


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TCheckbox property definitions and factory."""

    CS = TCheckbox.CheckboxSize

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="label", label="Label", prop_type="str", default="Checkbox",
            apply=lambda w, v: w._label.setText(str(v)),
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=CS.MEDIUM.value, options=_enum_options(CS),
            apply=lambda w, v: w.set_size(_to_enum(CS, v)),
        ),
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.set_disabled(bool(v)),
        ),
        PropertyDefinition(
            name="default_checked", label="Checked", prop_type="bool", default=False,
            apply=lambda w, v: w.set_state(
                TCheckbox.CheckState.CHECKED if v else TCheckbox.CheckState.UNCHECKED,
            ),
        ),
    ]

    registry.register("checkbox", definitions)
    registry.register_factory("checkbox", lambda: TCheckbox(label="Checkbox"))
