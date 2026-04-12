"""SliderShowcase: demonstrates TSlider single, range, marks, vertical, reverse, and keyboard modes."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TSlider


class SliderShowcase(BaseShowcase):
    """Showcase for the TSlider atom component.

    Sections: basic usage, range mode, marks, disabled, reverse, keyboard, mark snap.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        basic = TSlider(value=30, min_val=0, max_val=100, step=1, tooltip=True)
        basic.setMinimumWidth(300)
        self.add_section("Basic Usage", "Single-thumb slider with tooltip.", basic)

        # Range mode
        rng = TSlider(value=(20, 80), range=True, tooltip=True)
        rng.setMinimumWidth(300)
        self.add_section("Range Mode", "Dual-thumb range selection.", rng)

        # With marks
        marks_slider = TSlider(
            value=50, marks={0: "0", 25: "25", 50: "50", 75: "75", 100: "100"}, step=25,
        )
        marks_slider.setMinimumWidth(300)
        self.add_section("Marks", "Step snapping with labeled tick marks.", marks_slider)

        # Disabled
        disabled = TSlider(value=40, disabled=True)
        disabled.setMinimumWidth(300)
        self.add_section("Disabled", "Slider in disabled state.", disabled)

        # Reverse
        reverse_slider = TSlider(value=70, reverse=True, tooltip=True)
        reverse_slider.setMinimumWidth(300)
        self.add_section("Reverse", "Slider with reversed direction (right-to-left).", reverse_slider)

        # Keyboard navigation
        kb_slider = TSlider(value=50, keyboard=True, step=10, tooltip=True)
        kb_slider.setMinimumWidth(300)
        self.add_section(
            "Keyboard",
            "Focus the slider and use arrow keys to adjust value (step=10).",
            kb_slider,
        )

        # Mark snap (step='mark' snaps to nearest mark position)
        snap_slider = TSlider(
            value=0,
            marks={0: "Start", 30: "30%", 70: "70%", 100: "End"},
            step="mark",
            tooltip=True,
        )
        snap_slider.setMinimumWidth(300)
        self.add_section(
            "Mark Snap",
            "Step set to 'mark' \u2014 thumb snaps to nearest mark position only.",
            snap_slider,
        )
