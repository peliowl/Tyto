"""RadioShowcase: demonstrates TRadio, TRadioButton, and TRadioGroup features."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TRadio, TRadioButton, TRadioGroup


class RadioShowcase(BaseShowcase):
    """Showcase for the TRadio / TRadioButton / TRadioGroup atom components.

    Sections: basic usage, group mutual exclusion, sizes, disabled,
    RadioButton group.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "A single radio button.",
            self.hbox(TRadio("Option", value="opt")),
        )

        # Group mutual exclusion
        group = TRadioGroup()
        group.add_radio(TRadio("Option A", value="a"))
        group.add_radio(TRadio("Option B", value="b", checked=True))
        group.add_radio(TRadio("Option C", value="c"))

        self.add_section(
            "Group Mutual Exclusion",
            "Only one radio can be selected within a group.",
            group,
        )

        # Sizes
        self.add_section(
            "Sizes",
            "Small, Medium, and Large size variants.",
            self.hbox(
                TRadio("Small", value="s", size=TRadio.RadioSize.SMALL),
                TRadio("Medium", value="m", size=TRadio.RadioSize.MEDIUM),
                TRadio("Large", value="l", size=TRadio.RadioSize.LARGE),
            ),
        )

        # Disabled
        self.add_section(
            "Disabled",
            "Disabled radios have reduced opacity and block interaction.",
            self.hbox(
                TRadio("Disabled", value="d1", disabled=True),
                TRadio("Disabled Checked", value="d2", checked=True, disabled=True),
            ),
        )

        # RadioButton group
        btn_group = TRadioGroup()
        btn_group.add_radio(TRadioButton("Beijing", value="bj"))
        btn_group.add_radio(TRadioButton("Shanghai", value="sh", checked=True))
        btn_group.add_radio(TRadioButton("Guangzhou", value="gz"))

        self.add_section(
            "RadioButton Group",
            "Button-style radio group with segmented layout.",
            btn_group,
        )
