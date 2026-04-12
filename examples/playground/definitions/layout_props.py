"""Property definitions for TLayout in the Playground."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TLayout, TLayoutContent, TLayoutFooter, TLayoutHeader


def _make_layout() -> TLayout:
    """Create a default TLayout with header, content, and footer."""
    layout = TLayout()
    layout.setFixedHeight(300)
    header = TLayoutHeader(height=50)
    header.set_content(QLabel("Header"))
    layout.add_header(header)
    content = TLayoutContent()
    content.set_content(QLabel("Content"))
    layout.add_content(content)
    footer = TLayoutFooter(height=40)
    footer.set_content(QLabel("Footer"))
    layout.add_footer(footer)
    return layout


def register(registry: PropertyRegistry) -> None:
    """Register TLayout property definitions and factory."""

    definitions: list[PropertyDefinition] = []

    registry.register("layout", definitions)
    registry.register_factory("layout", _make_layout)
