"""Property definitions for TBackTop in the Playground."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TBackTop


def _make_backtop() -> QWidget:
    """Create a scrollable container with TBackTop attached."""
    # Outer container
    container = QWidget()
    container.setFixedSize(300, 300)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    # Scroll area with tall content
    scroll = QScrollArea(container)
    scroll.setWidgetResizable(True)
    scroll.setFixedSize(300, 300)

    inner = QWidget()
    inner_layout = QVBoxLayout(inner)
    for i in range(50):
        lbl = QLabel(f"Line {i + 1} \u2014 scroll down to see BackTop button")
        inner_layout.addWidget(lbl)
    scroll.setWidget(inner)

    layout.addWidget(scroll)

    # Attach BackTop to the scroll area
    backtop = TBackTop(target=scroll, visibility_height=100)
    # Store reference to prevent GC
    container._backtop = backtop  # type: ignore[attr-defined]

    return container


def register(registry: PropertyRegistry) -> None:
    """Register TBackTop property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="visibility_height", label="Visibility Height", prop_type="int", default=100,
            apply=lambda w, v: setattr(w._backtop, "visibility_height", int(v)) if hasattr(w, "_backtop") else None,
        ),
        PropertyDefinition(
            name="controlled_show", label="Controlled Show", prop_type="enum",
            default="auto",
            options=[("auto", "auto"), ("true", "true"), ("false", "false")],
            apply=lambda w, v: (
                setattr(w._backtop, "controlled_show", None) if v == "auto"
                else setattr(w._backtop, "controlled_show", v == "true")
            ) if hasattr(w, "_backtop") else None,
        ),
    ]

    registry.register("backtop", definitions)
    registry.register_factory("backtop", _make_backtop)
