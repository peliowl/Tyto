"""TagShowcase: demonstrates TTag types, sizes, round, checkable, and custom colors."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TTag


class TagShowcase(BaseShowcase):
    """Showcase for the TTag atom component.

    Sections: basic usage, color types, sizes, closable, tiny, info,
    round, checkable, custom color.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A simple default tag.",
            self.hbox(TTag("Tag")),
        )

        # Color types (including Info)
        self.add_section(
            "Color Types",
            "Default, Primary, Info, Success, Warning, and Error color variants.",
            self.hbox(
                TTag("Default", tag_type=TTag.TagType.DEFAULT),
                TTag("Primary", tag_type=TTag.TagType.PRIMARY),
                TTag("Info", tag_type=TTag.TagType.INFO),
                TTag("Success", tag_type=TTag.TagType.SUCCESS),
                TTag("Warning", tag_type=TTag.TagType.WARNING),
                TTag("Error", tag_type=TTag.TagType.ERROR),
            ),
        )

        # Sizes (including Tiny)
        self.add_section(
            "Sizes",
            "Tiny, Small, Medium, and Large size variants.",
            self.hbox(
                TTag("Tiny", size=TTag.TagSize.TINY),
                TTag("Small", size=TTag.TagSize.SMALL),
                TTag("Medium", size=TTag.TagSize.MEDIUM),
                TTag("Large", size=TTag.TagSize.LARGE),
            ),
        )

        # Closable
        self.add_section(
            "Closable",
            "Tags with a close button that emits the closed signal.",
            self.hbox(
                TTag("Closable", tag_type=TTag.TagType.PRIMARY, closable=True),
                TTag("Closable", tag_type=TTag.TagType.SUCCESS, closable=True),
                TTag("Closable", tag_type=TTag.TagType.ERROR, closable=True),
            ),
        )

        # Round
        self.add_section(
            "Round",
            "Fully rounded (capsule-shaped) tags.",
            self.hbox(
                TTag("Round", tag_type=TTag.TagType.PRIMARY, round=True),
                TTag("Round", tag_type=TTag.TagType.INFO, round=True),
                TTag("Round", tag_type=TTag.TagType.SUCCESS, round=True),
            ),
        )

        # Checkable
        self.add_section(
            "Checkable",
            "Click to toggle the checked state of the tag.",
            self.hbox(
                TTag("Checkable", tag_type=TTag.TagType.PRIMARY, checkable=True),
                TTag("Checked", tag_type=TTag.TagType.SUCCESS, checkable=True, checked=True),
                TTag("Unchecked", tag_type=TTag.TagType.INFO, checkable=True),
            ),
        )

        # Custom color
        self.add_section(
            "Custom Color",
            "Tags with custom color, border_color, and text_color overrides.",
            self.hbox(
                TTag(
                    "Custom",
                    color={"color": "#8b5cf6", "border_color": "#7c3aed", "text_color": "#ffffff"},
                ),
                TTag(
                    "Custom",
                    color={"color": "#f97316", "border_color": "#ea580c", "text_color": "#ffffff"},
                ),
            ),
        )
