"""SpinShowcase: demonstrates TSpin modes, animation types, sizes, and enhancements."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TSpin


class SpinShowcase(BaseShowcase):
    """Showcase for the TSpin atom component.

    Sections: basic usage, animation types, sizes, nested mode, description,
    custom icon, stroke customization, numeric size.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "Standalone spinning indicator.",
            self.hbox(TSpin(spinning=True)),
        )

        # Animation types
        self.add_section(
            "Animation Types",
            "Ring, dots, and pulse animation styles.",
            self.hbox(
                TSpin(animation_type=TSpin.AnimationType.RING),
                TSpin(animation_type=TSpin.AnimationType.DOTS),
                TSpin(animation_type=TSpin.AnimationType.PULSE),
            ),
        )

        # Sizes
        self.add_section(
            "Sizes",
            "Small, medium, and large size variants.",
            self.hbox(
                TSpin(size=TSpin.SpinSize.SMALL),
                TSpin(size=TSpin.SpinSize.MEDIUM),
                TSpin(size=TSpin.SpinSize.LARGE),
            ),
        )

        # Nested mode
        content = QLabel("Wrapped content area")
        content.setFixedSize(200, 80)
        nested = TSpin(mode=TSpin.SpinMode.NESTED, spinning=True)
        nested.set_content(content)
        self.add_section(
            "Nested Mode",
            "Overlay spinner on child content.",
            nested,
        )

        # With description
        self.add_section(
            "Description",
            "Display loading text below the animation.",
            self.hbox(TSpin(description="Loading...")),
        )

        # Custom icon (replace default indicator with a QLabel as icon)
        custom_icon_spin = TSpin(spinning=True)
        icon_label = QLabel("\u23f3")
        icon_label.setFixedSize(28, 28)
        custom_icon_spin.set_icon(icon_label)
        custom_icon_spin.set_rotate(True)
        self.add_section(
            "Custom Icon",
            "Replace the default indicator with a custom widget. Rotate enabled.",
            self.hbox(custom_icon_spin),
        )

        # Stroke customization
        self.add_section(
            "Stroke Customization",
            "Custom stroke width and color for the ring animation.",
            self.hbox(
                TSpin(spinning=True, stroke_width=4, stroke="#d03050"),
                TSpin(spinning=True, stroke_width=2, stroke="#2080f0"),
                TSpin(spinning=True, stroke_width=6, stroke="#f0a020"),
            ),
        )

        # Numeric size (integer pixel value instead of enum)
        self.add_section(
            "Numeric Size",
            "Specify animation size as an integer pixel value (e.g. 48px).",
            self.hbox(
                TSpin(size=24, spinning=True),
                TSpin(size=48, spinning=True),
                TSpin(size=72, spinning=True),
            ),
        )
