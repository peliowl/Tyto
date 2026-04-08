"""ButtonShowcase: demonstrates TButton types, sizes, shapes, ghost, block, icon, and more."""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton


def _make_icon(char: str, size: int = 16, color: QColor | None = None) -> QIcon:
    """Create a QIcon by rendering a single Unicode character onto a pixmap."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    if color is not None:
        painter.setPen(color)
    else:
        painter.setPen(QColor("#ffffff"))
    font = QFont()
    font.setPixelSize(int(size * 0.75))
    painter.setFont(font)
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(px)


class ButtonShowcase(BaseShowcase):
    """Showcase for the TButton atom component.

    Sections: basic usage, types, extended types, sizes, circle/round,
    ghost, block, icon, loading, disabled.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A simple default button.",
            self.hbox(TButton("Button")),
        )

        # Types
        self.add_section(
            "Types",
            "Primary, Default, Dashed, and Text button types.",
            self.hbox(
                TButton("Primary", button_type=TButton.ButtonType.PRIMARY),
                TButton("Default", button_type=TButton.ButtonType.DEFAULT),
                TButton("Dashed", button_type=TButton.ButtonType.DASHED),
                TButton("Text", button_type=TButton.ButtonType.TEXT),
            ),
        )

        # Extended types
        self.add_section(
            "Extended Types",
            "Info, Success, Warning, Error, and Tertiary type variants.",
            self.hbox(
                TButton("Info", button_type=TButton.ButtonType.INFO),
                TButton("Success", button_type=TButton.ButtonType.SUCCESS),
                TButton("Warning", button_type=TButton.ButtonType.WARNING),
                TButton("Error", button_type=TButton.ButtonType.ERROR),
                TButton("Tertiary", button_type=TButton.ButtonType.TERTIARY),
            ),
        )

        # Sizes
        self.add_section(
            "Sizes",
            "Tiny, Small, Medium, and Large size variants.",
            self.hbox(
                TButton("Tiny", size=TButton.ButtonSize.TINY),
                TButton("Small", size=TButton.ButtonSize.SMALL),
                TButton("Medium", size=TButton.ButtonSize.MEDIUM),
                TButton("Large", size=TButton.ButtonSize.LARGE),
            ),
        )

        # Circle and Round
        self.add_section(
            "Circle & Round",
            "Circle buttons render as perfect circles; round buttons have capsule shape.",
            self.hbox(
                TButton("C", button_type=TButton.ButtonType.PRIMARY, circle=True),
                TButton("C", button_type=TButton.ButtonType.DEFAULT, circle=True),
                TButton("Round Primary", button_type=TButton.ButtonType.PRIMARY, round=True),
                TButton("Round Default", button_type=TButton.ButtonType.DEFAULT, round=True),
            ),
        )

        # Ghost
        self.add_section(
            "Ghost",
            "Ghost buttons have transparent background with colored border and text.",
            self.hbox(
                TButton("Primary", button_type=TButton.ButtonType.PRIMARY, ghost=True),
                TButton("Info", button_type=TButton.ButtonType.INFO, ghost=True),
                TButton("Success", button_type=TButton.ButtonType.SUCCESS, ghost=True),
                TButton("Warning", button_type=TButton.ButtonType.WARNING, ghost=True),
                TButton("Error", button_type=TButton.ButtonType.ERROR, ghost=True),
            ),
        )

        # Block
        block_container = QWidget()
        block_layout = QVBoxLayout(block_container)
        block_layout.setContentsMargins(0, 0, 0, 2)
        block_layout.setSpacing(8)
        block_layout.addWidget(TButton("Block Primary", button_type=TButton.ButtonType.PRIMARY, block=True))
        block_layout.addWidget(TButton("Block Default", button_type=TButton.ButtonType.DEFAULT, block=True))

        self.add_section(
            "Block",
            "Block buttons expand to fill the parent container width.",
            block_container,
        )

        # Icon buttons
        search_icon = _make_icon("🔍", 16, QColor("#ffffff"))
        arrow_icon = _make_icon("→", 16, QColor("#333639"))
        self.add_section(
            "Icon Buttons",
            "Buttons with icons placed on the left or right side of the text.",
            self.hbox(
                TButton("Search", button_type=TButton.ButtonType.PRIMARY, icon=search_icon),
                TButton(
                    "Next",
                    button_type=TButton.ButtonType.DEFAULT,
                    icon=arrow_icon,
                    icon_placement=TButton.IconPlacement.RIGHT,
                ),
            ),
        )

        # Loading
        self.add_section(
            "Loading",
            "Buttons in loading state show a spinner and block clicks.",
            self.hbox(
                TButton("Loading", button_type=TButton.ButtonType.PRIMARY, loading=True),
                TButton("Loading", button_type=TButton.ButtonType.DEFAULT, loading=True),
            ),
        )

        # Disabled
        self.add_section(
            "Disabled",
            "Disabled buttons have reduced opacity and block interaction.",
            self.hbox(
                TButton("Disabled", button_type=TButton.ButtonType.PRIMARY, disabled=True),
                TButton("Disabled", button_type=TButton.ButtonType.DEFAULT, disabled=True),
            ),
        )
