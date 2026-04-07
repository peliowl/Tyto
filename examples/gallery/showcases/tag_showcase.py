"""TagShowcase: demonstrates TTag types, sizes, and closable."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TTag


class TagShowcase(BaseShowcase):
    """Showcase for the TTag atom component.

    Sections: basic usage, color types, sizes, closable.

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

        # Color types
        self.add_section(
            "Color Types",
            "Default, Primary, Success, Warning, and Error color variants.",
            self.hbox(
                TTag("Default", tag_type=TTag.TagType.DEFAULT),
                TTag("Primary", tag_type=TTag.TagType.PRIMARY),
                TTag("Success", tag_type=TTag.TagType.SUCCESS),
                TTag("Warning", tag_type=TTag.TagType.WARNING),
                TTag("Error", tag_type=TTag.TagType.ERROR),
            ),
        )

        # Sizes
        self.add_section(
            "Sizes",
            "Small, Medium, and Large size variants.",
            self.hbox(
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
