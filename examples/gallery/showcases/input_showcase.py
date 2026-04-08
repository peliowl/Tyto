"""InputShowcase: demonstrates TInput features including sizes, textarea, count, status, and round."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TInput


class InputShowcase(BaseShowcase):
    """Showcase for the TInput atom component.

    Sections: basic usage, clearable, password mode, sizes, textarea,
    show count, validation status, round.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A simple text input field.",
            TInput(placeholder="Enter text..."),
        )

        # Clearable
        self.add_section(
            "Clearable",
            "Shows a clear button when text is present.",
            TInput(placeholder="Type and clear...", clearable=True),
        )

        # Password mode
        self.add_section(
            "Password Mode",
            "Masks input text with a visibility toggle button.",
            TInput(placeholder="Password", password=True),
        )

        # Sizes
        self.add_section(
            "Sizes",
            "Tiny, Small, Medium, and Large size variants.",
            self.hbox(
                TInput(placeholder="Tiny", size=TInput.InputSize.TINY),
                TInput(placeholder="Small", size=TInput.InputSize.SMALL),
                TInput(placeholder="Medium", size=TInput.InputSize.MEDIUM),
                TInput(placeholder="Large", size=TInput.InputSize.LARGE),
            ),
        )

        # Textarea mode
        self.add_section(
            "Textarea",
            "Multi-line text input area with configurable rows.",
            TInput(placeholder="Enter multi-line text...", input_type=TInput.InputType.TEXTAREA, rows=4),
        )

        # Show count
        self.add_section(
            "Character Count",
            "Displays current / max character count below the input.",
            self.hbox(
                TInput(placeholder="Max 50 chars", maxlength=50, show_count=True),
                TInput(
                    placeholder="Textarea with count",
                    input_type=TInput.InputType.TEXTAREA,
                    maxlength=200,
                    show_count=True,
                    rows=3,
                ),
            ),
        )

        # Validation status
        self.add_section(
            "Validation Status",
            "Success, Warning, and Error status variants change the border color.",
            self.hbox(
                TInput(placeholder="Success", status=TInput.InputStatus.SUCCESS),
                TInput(placeholder="Warning", status=TInput.InputStatus.WARNING),
                TInput(placeholder="Error", status=TInput.InputStatus.ERROR),
            ),
        )

        # Round
        self.add_section(
            "Round",
            "Fully rounded (capsule-shaped) input field.",
            TInput(placeholder="Round input", round=True),
        )
