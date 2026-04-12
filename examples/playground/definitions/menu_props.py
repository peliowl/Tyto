"""Property definitions for TMenu in the Playground."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TMenu, TMenuItem, TMenuItemGroup


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _apply_icon(w: Any, v: Any) -> None:
    """Apply icon from a file path to all menu items and groups, or clear if empty."""
    path = str(v) if v else ""
    icon = QIcon(path) if path else None

    def _apply_recursive(items: list[Any]) -> None:
        for item in items:
            if isinstance(item, TMenuItem):
                item.set_icon(icon)
            elif isinstance(item, TMenuItemGroup):
                item.set_icon(icon)
                _apply_recursive(item.get_items())

    _apply_recursive(getattr(w, "_items", []))
    w.updateGeometry()
    w.adjustSize()


def _apply_container_height(w: Any, v: Any) -> None:
    """Set the height of the menu's parent container in the preview panel.

    Clears the layout-level AlignTop constraint and trailing stretch so
    the vertical menu can expand to fill the container height.
    """
    height = int(v) if v else 0
    parent = w.parentWidget()
    if parent is None:
        return
    layout = parent.layout()
    if height > 0:
        parent.setFixedHeight(height)
        if layout is not None:
            # Clear layout-level alignment (AlignTop|AlignLeft) that
            # constrains children to their sizeHint
            layout.setAlignment(Qt.AlignmentFlag(0))
            # Remove trailing stretch items that prevent expansion
            for i in range(layout.count() - 1, -1, -1):
                item = layout.itemAt(i)
                if item is not None and item.widget() is None and item.spacerItem() is not None:
                    layout.removeItem(item)
    else:
        # Reset to default (no fixed height)
        parent.setMinimumHeight(0)
        parent.setMaximumHeight(16777215)


def _make_menu() -> TMenu:
    """Create a default TMenu with sample items and nested groups.

    The menu is created in vertical mode so the built-in collapse toggle
    button is visible by default.  A minimum height is set to ensure the
    toggle button (vertically centred) has enough room to render.
    """
    menu = TMenu(mode=TMenu.MenuMode.VERTICAL, active_key="home")
    menu.add_item(TMenuItem(key="home", label="Home"))

    # Level-2 sub-group nested inside "Content" to demonstrate 3-level menu
    articles_group = TMenuItemGroup(key="articles", label="Articles")
    articles_group.add_item(TMenuItem(key="tech", label="Tech"))
    articles_group.add_item(TMenuItem(key="design", label="Design"))

    group = TMenuItemGroup(key="content", label="Content")
    group.add_item(articles_group)
    group.add_item(TMenuItem(key="categories", label="Categories"))
    menu.add_item(group)

    menu.add_item(TMenuItem(key="settings", label="Settings"))
    menu.setFixedWidth(220)
    return menu


def register(registry: PropertyRegistry) -> None:
    """Register TMenu property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="mode", label="Mode", prop_type="enum",
            default=TMenu.MenuMode.VERTICAL.value,
            options=_enum_options(TMenu.MenuMode),
            apply=lambda w, v: w.set_mode(TMenu.MenuMode(v)),
        ),
        PropertyDefinition(
            name="icon", label="Icon", prop_type="file", default="",
            apply=_apply_icon,
        ),
        PropertyDefinition(
            name="collapsed", label="Collapsed", prop_type="bool", default=False,
            apply=lambda w, v: w.set_collapsed(bool(v)),
        ),
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.set_disabled(bool(v)),
        ),
        PropertyDefinition(
            name="container_height", label="Container Height", prop_type="int",
            default=400,
            apply=_apply_container_height,
        ),
    ]

    registry.register("menu", definitions)
    registry.register_factory("menu", _make_menu)
