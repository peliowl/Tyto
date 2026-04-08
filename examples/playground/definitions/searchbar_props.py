"""Property definitions for TSearchBar in the Playground."""

from __future__ import annotations

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TSearchBar


def register(registry: PropertyRegistry) -> None:
    """Register TSearchBar property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="placeholder", label="Placeholder", prop_type="str",
            default="搜索...",
            apply=lambda w, v: (
                w._input._line_edit.setPlaceholderText(str(v)) if w._input._line_edit else None
            ),
        ),
        PropertyDefinition(
            name="clearable", label="Clearable", prop_type="bool", default=True,
        ),
    ]

    registry.register("searchbar", definitions)
    registry.register_factory("searchbar", lambda: TSearchBar())
