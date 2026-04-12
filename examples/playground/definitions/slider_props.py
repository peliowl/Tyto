"""Property definitions for TSlider in the Playground."""

from __future__ import annotations

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TSlider


def register(registry: PropertyRegistry) -> None:
    """Register TSlider property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.set_disabled(bool(v)),
        ),
        PropertyDefinition(
            name="tooltip", label="Tooltip", prop_type="bool", default=True,
            apply=lambda w, v: w.set_tooltip(bool(v)),
        ),
        PropertyDefinition(
            name="step", label="Step", prop_type="int", default=1,
            apply=lambda w, v: w.set_step(int(v)) if int(v) > 0 else None,
        ),
        PropertyDefinition(
            name="reverse", label="Reverse", prop_type="bool", default=False,
            apply=lambda w, v: w.set_reverse(bool(v)),
        ),
        PropertyDefinition(
            name="keyboard", label="Keyboard", prop_type="bool", default=True,
            apply=lambda w, v: w.set_keyboard(bool(v)),
        ),
    ]

    registry.register("slider", definitions)
    registry.register_factory("slider", lambda: TSlider(value=30, tooltip=True))
