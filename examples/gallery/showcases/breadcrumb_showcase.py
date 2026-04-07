"""BreadcrumbShowcase: demonstrates TBreadcrumb features."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import BreadcrumbItem, TBreadcrumb


class BreadcrumbShowcase(BaseShowcase):
    """Showcase for the TBreadcrumb molecule component.

    Sections: basic usage, custom separator.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "Navigation path with clickable items (last item is current location).",
            TBreadcrumb(items=[
                BreadcrumbItem("Home", "/"),
                BreadcrumbItem("Components", "/components"),
                BreadcrumbItem("Breadcrumb", "/components/breadcrumb"),
            ]),
        )

        # Custom separator
        self.add_section(
            "Custom Separator",
            "Breadcrumb with a custom separator string.",
            TBreadcrumb(
                items=[
                    BreadcrumbItem("Home", "/"),
                    BreadcrumbItem("Settings", "/settings"),
                    BreadcrumbItem("Profile", "/settings/profile"),
                ],
                separator=" > ",
            ),
        )
