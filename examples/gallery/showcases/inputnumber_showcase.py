"""InputNumberShowcase: demonstrates TInputNumber step, range, precision, sizes, and enhancements."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TInputNumber


class InputNumberShowcase(BaseShowcase):
    """Showcase for the TInputNumber atom component.

    Sections: basic usage, sizes, precision, range limits, disabled,
    button placement, loading, clearable, status, round.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.add_section(
            "Basic Usage",
            "Numeric input with +/- buttons and keyboard arrows.",
            self.hbox(TInputNumber(value=5, step=1)),
        )

        self.add_section(
            "Sizes",
            "Small, medium, and large size variants.",
            self.hbox(
                TInputNumber(value=1, size=TInputNumber.InputNumberSize.SMALL),
                TInputNumber(value=2, size=TInputNumber.InputNumberSize.MEDIUM),
                TInputNumber(value=3, size=TInputNumber.InputNumberSize.LARGE),
            ),
        )

        self.add_section(
            "Precision",
            "Decimal precision control (2 decimal places, step 0.1).",
            self.hbox(TInputNumber(value=3.14, step=0.1, precision=2)),
        )

        self.add_section(
            "Range Limits",
            "Value constrained between 0 and 10.",
            self.hbox(TInputNumber(value=5, min=0, max=10, step=1)),
        )

        self.add_section(
            "Disabled",
            "Disabled numeric input.",
            self.hbox(TInputNumber(value=42, disabled=True)),
        )

        # Button placement
        self.add_section(
            "Button Placement",
            "Buttons on the right (default) vs. both sides.",
            self.hbox(
                TInputNumber(value=5, button_placement="right"),
                TInputNumber(value=5, button_placement="both"),
            ),
        )

        # Loading
        self.add_section(
            "Loading",
            "Loading state with spinner indicator.",
            self.hbox(TInputNumber(value=10, loading=True)),
        )

        # Clearable
        self.add_section(
            "Clearable",
            "Show a clear button when the input has a value.",
            self.hbox(TInputNumber(value=99, clearable=True)),
        )

        # Status
        self.add_section(
            "Status",
            "Validation status variants: success, warning, error.",
            self.hbox(
                TInputNumber(value=1, status=TInputNumber.InputNumberStatus.SUCCESS),
                TInputNumber(value=2, status=TInputNumber.InputNumberStatus.WARNING),
                TInputNumber(value=3, status=TInputNumber.InputNumberStatus.ERROR),
            ),
        )

        # Round
        self.add_section(
            "Round",
            "Fully rounded (capsule) input number.",
            self.hbox(TInputNumber(value=7, round=True)),
        )
