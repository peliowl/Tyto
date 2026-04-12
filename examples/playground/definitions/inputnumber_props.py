"""Property definitions for TInputNumber in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TInputNumber


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def register(registry: PropertyRegistry) -> None:
    """Register TInputNumber property definitions and factory."""

    INS = TInputNumber.InputNumberSize
    INST = TInputNumber.InputNumberStatus

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=INS.MEDIUM.value, options=_enum_options(INS),
            apply=lambda w, v: w.set_size(_to_enum(INS, v)),
        ),
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.set_disabled(bool(v)),
        ),
        PropertyDefinition(
            name="button_placement", label="Button Placement", prop_type="enum",
            default="right", options=[("right", "right"), ("both", "both")],
            apply=lambda w, v: w.set_button_placement(str(v)),
        ),
        PropertyDefinition(
            name="loading", label="Loading", prop_type="bool", default=False,
            apply=lambda w, v: w.set_loading(bool(v)),
        ),
        PropertyDefinition(
            name="clearable", label="Clearable", prop_type="bool", default=False,
            apply=lambda w, v: w.set_clearable(bool(v)),
        ),
        PropertyDefinition(
            name="status", label="Status", prop_type="enum",
            default="", options=[("", "none")] + _enum_options(INST),
            apply=lambda w, v: w.set_status(_to_enum(INST, v) if v else None),
        ),
        PropertyDefinition(
            name="round", label="Round", prop_type="bool", default=False,
            apply=lambda w, v: w.set_round(bool(v)),
        ),
        PropertyDefinition(
            name="bordered", label="Bordered", prop_type="bool", default=True,
            apply=lambda w, v: w.set_bordered(bool(v)),
        ),
        PropertyDefinition(
            name="width", label="Width", prop_type="int", default=180,
            apply=lambda w, v: w.setFixedWidth(int(v)) if int(v) > 0 else None,
        ),
    ]

    registry.register("inputnumber", definitions)
    registry.register_factory("inputnumber", lambda: TInputNumber(value=0, step=1))
