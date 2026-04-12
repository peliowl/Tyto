"""MenuShowcase: demonstrates TMenu vertical, horizontal, and nested groups."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TMenu, TMenuItem, TMenuItemGroup


class MenuShowcase(BaseShowcase):
    """Showcase for the TMenu organism component.

    Sections: vertical menu, horizontal menu, nested groups.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Vertical menu
        vmenu = TMenu(mode=TMenu.MenuMode.VERTICAL, active_key="home")
        vmenu.add_item(TMenuItem(key="home", label="Home"))
        vmenu.add_item(TMenuItem(key="about", label="About"))
        vmenu.add_item(TMenuItem(key="contact", label="Contact"))
        vmenu.setFixedWidth(200)
        self.add_section("Vertical", "Standard vertical navigation menu.", vmenu)

        # Horizontal menu
        hmenu = TMenu(mode=TMenu.MenuMode.HORIZONTAL, active_key="dashboard")
        hmenu.add_item(TMenuItem(key="dashboard", label="Dashboard"))
        hmenu.add_item(TMenuItem(key="settings", label="Settings"))
        hmenu.add_item(TMenuItem(key="help", label="Help"))
        self.add_section("Horizontal", "Horizontal navigation bar.", hmenu)

        # Nested groups
        nested = TMenu(mode=TMenu.MenuMode.VERTICAL, active_key="profile")
        nested.setFixedWidth(220)

        group = TMenuItemGroup(key="user", label="User")
        group.add_item(TMenuItem(key="profile", label="Profile"))
        group.add_item(TMenuItem(key="preferences", label="Preferences"))
        nested.add_item(group)

        group2 = TMenuItemGroup(key="admin", label="Admin")
        group2.add_item(TMenuItem(key="users", label="Users"))
        group2.add_item(TMenuItem(key="roles", label="Roles"))
        nested.add_item(group2)

        self.add_section("Nested Groups", "Menu with expandable sub-groups.", nested)
