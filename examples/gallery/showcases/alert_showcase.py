"""AlertShowcase: demonstrates TAlert types, closable, no border, default type, and show_icon."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TAlert


class AlertShowcase(BaseShowcase):
    """Showcase for the TAlert molecule component.

    Sections: basic types, closable, no border, default type, show icon toggle.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic types
        types_container = QWidget()
        types_layout = QVBoxLayout(types_container)
        types_layout.setContentsMargins(0, 0, 0, 0)
        types_layout.setSpacing(8)
        for at in TAlert.AlertType:
            types_layout.addWidget(
                TAlert(
                    alert_type=at,
                    title=at.value.capitalize(),
                    description=f"This is a {at.value} alert.",
                )
            )
        self.add_section(
            "Types",
            "Default, success, info, warning, and error alert types.",
            types_container,
        )

        # Closable
        self.add_section(
            "Closable",
            "Alert with a close button.",
            TAlert(
                alert_type=TAlert.AlertType.INFO,
                title="Closable",
                description="Click X to dismiss.",
                closable=True,
            ),
        )

        # No border
        self.add_section(
            "No Border",
            "Alert without the left accent border.",
            TAlert(
                alert_type=TAlert.AlertType.WARNING,
                title="No Border",
                bordered=False,
            ),
        )

        # Default type
        self.add_section(
            "Default Type",
            "The default alert type with neutral styling.",
            TAlert(
                alert_type=TAlert.AlertType.DEFAULT,
                title="Default Alert",
                description="A neutral alert without semantic color.",
            ),
        )

        # Show icon toggle
        self.add_section(
            "Hide Icon",
            "Alert with the icon area hidden (show_icon=False).",
            TAlert(
                alert_type=TAlert.AlertType.SUCCESS,
                title="No Icon",
                description="This alert has no icon.",
                show_icon=False,
            ),
        )
