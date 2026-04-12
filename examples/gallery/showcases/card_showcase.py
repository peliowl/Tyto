"""CardShowcase: demonstrates TCard sizes, hoverable, bordered, closable."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TCard


class CardShowcase(BaseShowcase):
    """Showcase for the TCard organism component.

    Sections: basic usage, sizes, hoverable, closable.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        card = TCard(title="Basic Card")
        card.set_content(QLabel("Card body content goes here."))
        self.add_section("Basic Usage", "Simple card with title and content.", card)

        # Sizes
        cards = []
        for sz in TCard.CardSize:
            c = TCard(title=f"{sz.value.capitalize()} Card", size=sz)
            c.set_content(QLabel(f"Size: {sz.value}"))
            cards.append(c)
        self.add_section("Sizes", "Small, medium, and large card sizes.", self.hbox(*cards))

        # Hoverable
        hover_card = TCard(title="Hoverable", hoverable=True)
        hover_card.set_content(QLabel("Hover to deepen shadow."))
        self.add_section("Hoverable", "Shadow deepens on mouse hover.", hover_card)

        # Closable
        close_card = TCard(title="Closable", closable=True)
        close_card.set_content(QLabel("Click X to close."))
        self.add_section("Closable", "Card with a close button.", close_card)
