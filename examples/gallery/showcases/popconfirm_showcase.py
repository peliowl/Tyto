"""PopconfirmShowcase: demonstrates TPopconfirm basic usage, placement, trigger modes, and button customization."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton, TPopconfirm


class PopconfirmShowcase(BaseShowcase):
    """Showcase for the TPopconfirm molecule component.

    Sections: basic usage, placement variants, trigger modes, button customization.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        btn = TButton(text="Delete")
        pop = TPopconfirm(trigger=btn, title="Are you sure?")
        self.add_section(
            "Basic Usage",
            "Click the button to show a confirmation popover.",
            pop,
        )

        # Placement variants
        placements = []
        for p in TPopconfirm.Placement:
            b = TButton(text=p.value.capitalize())
            pc = TPopconfirm(trigger=b, title=f"Confirm ({p.value})?", placement=p)
            placements.append(pc)
        self.add_section(
            "Placement",
            "Popup position relative to the trigger.",
            self.hbox(*placements),
        )

        # Trigger modes
        hover_btn = TButton(text="Hover Me")
        hover_pop = TPopconfirm(trigger=hover_btn, title="Hover triggered", trigger_mode="hover")
        focus_btn = TButton(text="Focus Me")
        focus_pop = TPopconfirm(trigger=focus_btn, title="Focus triggered", trigger_mode="focus")
        self.add_section(
            "Trigger Modes",
            "Hover and focus trigger modes (default is click).",
            self.hbox(hover_pop, focus_pop),
        )

        # Button customization
        custom_btn = TButton(text="Custom Buttons")
        custom_pop = TPopconfirm(
            trigger=custom_btn,
            title="Proceed with action?",
            confirm_text="Yes, do it",
            cancel_text="Nope",
            positive_button_props={"button_type": "primary"},
            negative_button_props={"button_type": "default"},
        )
        self.add_section(
            "Button Customization",
            "Custom confirm/cancel text and button props.",
            custom_pop,
        )
