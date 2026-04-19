"""BackTopShowcase: demonstrates TBackTop with scrollable area and controlled visibility."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TBackTop


class BackTopShowcase(BaseShowcase):
    """Showcase for the TBackTop atom component.

    Sections: basic usage, controlled visibility.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Build a scrollable area with enough content to scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(250)

        container = QWidget()
        layout = QVBoxLayout(container)
        for i in range(30):
            layout.addWidget(QLabel(f"Scroll content line {i + 1}"))
        scroll.setWidget(container)

        backtop = TBackTop(target=scroll, visibility_height=100)

        self.add_section(
            "Basic Usage",
            "Scroll down to reveal the back-to-top button.",
            scroll,
        )

        # Controlled visibility (show=True forces the button to always be visible)
        scroll2 = QScrollArea()
        scroll2.setWidgetResizable(True)
        scroll2.setFixedHeight(200)

        container2 = QWidget()
        layout2 = QVBoxLayout(container2)
        for i in range(20):
            layout2.addWidget(QLabel(f"Content line {i + 1}"))
        scroll2.setWidget(container2)

        backtop_forced = TBackTop(target=scroll2, show=True)

        self.add_section(
            "Controlled Show",
            "BackTop forced visible via show=True, regardless of scroll position.",
            scroll2,
        )
