"""CheckboxShowcase: demonstrates TCheckbox states, sizes, disabled, and TCheckboxGroup."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TCheckbox, TCheckboxGroup


class CheckboxShowcase(BaseShowcase):
    """Showcase for the TCheckbox and TCheckboxGroup atom components.

    Sections: basic usage, three states, sizes, disabled, CheckboxGroup.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        self.add_section(
            "Basic Usage",
            "Click to toggle between checked and unchecked.",
            self.hbox(
                TCheckbox("Unchecked"),
                TCheckbox("Checked", state=TCheckbox.CheckState.CHECKED),
            ),
        )

        # Three states
        self.add_section(
            "Three States",
            "Checkbox supports Unchecked, Checked, and Indeterminate states.",
            self.hbox(
                TCheckbox("Unchecked", state=TCheckbox.CheckState.UNCHECKED),
                TCheckbox("Checked", state=TCheckbox.CheckState.CHECKED),
                TCheckbox("Indeterminate", state=TCheckbox.CheckState.INDETERMINATE),
            ),
        )

        # Sizes
        self.add_section(
            "Sizes",
            "Small, Medium, and Large size variants.",
            self.hbox(
                TCheckbox("Small", size=TCheckbox.CheckboxSize.SMALL),
                TCheckbox("Medium", size=TCheckbox.CheckboxSize.MEDIUM),
                TCheckbox("Large", size=TCheckbox.CheckboxSize.LARGE),
            ),
        )

        # Disabled
        self.add_section(
            "Disabled",
            "Disabled checkboxes have reduced opacity and block interaction.",
            self.hbox(
                TCheckbox("Disabled Unchecked", disabled=True),
                TCheckbox("Disabled Checked", state=TCheckbox.CheckState.CHECKED, disabled=True),
            ),
        )

        # CheckboxGroup
        group = TCheckboxGroup(min=1, max=3)
        group.add_checkbox(TCheckbox("Apple", value="apple", default_checked=True))
        group.add_checkbox(TCheckbox("Banana", value="banana"))
        group.add_checkbox(TCheckbox("Cherry", value="cherry"))
        group.add_checkbox(TCheckbox("Durian", value="durian"))

        self.add_section(
            "Checkbox Group",
            "A group with min=1 and max=3 selection constraints.",
            group,
        )
