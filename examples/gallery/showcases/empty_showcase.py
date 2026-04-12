"""EmptyShowcase: demonstrates TEmpty default, custom description, extra action, and enhancements."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton, TEmpty


class EmptyShowcase(BaseShowcase):
    """Showcase for the TEmpty atom component.

    Sections: basic usage, custom description, extra action, size variants, display control.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.add_section(
            "Basic Usage",
            "Default empty state placeholder.",
            TEmpty(),
        )

        self.add_section(
            "Custom Description",
            "Empty state with custom text.",
            TEmpty(description="No results found"),
        )

        # With extra action
        empty_action = TEmpty(description="Nothing here yet")
        empty_action.set_extra(TButton(text="Create New"))
        self.add_section(
            "Extra Action",
            "Empty state with an action button below.",
            empty_action,
        )

        # Size variants
        self.add_section(
            "Size Variants",
            "Tiny, small, medium, large, and huge size variants.",
            self.hbox(
                TEmpty(size=TEmpty.EmptySize.TINY, description="Tiny"),
                TEmpty(size=TEmpty.EmptySize.SMALL, description="Small"),
                TEmpty(size=TEmpty.EmptySize.MEDIUM, description="Medium"),
                TEmpty(size=TEmpty.EmptySize.LARGE, description="Large"),
            ),
        )

        # Display control
        no_icon = TEmpty(description="Description only, icon hidden.", show_icon=False)
        self.add_section(
            "Hide Icon",
            "Empty state with the icon area hidden.",
            no_icon,
        )

        no_desc = TEmpty(show_description=False)
        self.add_section(
            "Hide Description",
            "Empty state with the description text hidden.",
            no_desc,
        )
