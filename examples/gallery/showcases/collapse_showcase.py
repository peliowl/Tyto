"""CollapseShowcase: demonstrates TCollapse basic, accordion, arrow placement, trigger areas, and custom title."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton, TCollapse, TCollapseItem


class CollapseShowcase(BaseShowcase):
    """Showcase for the TCollapse molecule component.

    Sections: basic usage, accordion mode, arrow placement, trigger areas, custom title.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        collapse = TCollapse()
        for i in range(3):
            item = TCollapseItem(title=f"Panel {i + 1}", name=f"panel-{i + 1}")
            item.set_content(QLabel(f"Content of panel {i + 1}"))
            collapse.add_item(item)
        self.add_section(
            "Basic Usage",
            "Multiple panels that can be expanded independently.",
            collapse,
        )

        # Accordion mode
        accordion = TCollapse(accordion=True)
        for i in range(3):
            item = TCollapseItem(title=f"Accordion {i + 1}", name=f"acc-{i + 1}")
            item.set_content(QLabel(f"Only one panel open at a time. Panel {i + 1}."))
            accordion.add_item(item)
        self.add_section(
            "Accordion",
            "Only one panel can be expanded at a time.",
            accordion,
        )

        # Arrow placement (right)
        right_arrow = TCollapse(arrow_placement="right")
        for i in range(2):
            item = TCollapseItem(title=f"Right Arrow {i + 1}", name=f"ra-{i + 1}")
            item.set_content(QLabel(f"Arrow on the right side. Panel {i + 1}."))
            right_arrow.add_item(item)
        self.add_section(
            "Arrow Placement",
            "Arrow icon positioned on the right side of the header.",
            right_arrow,
        )

        # Trigger areas (arrow only)
        arrow_only = TCollapse(trigger_areas=["arrow"])
        for i in range(2):
            item = TCollapseItem(title=f"Arrow-Only Trigger {i + 1}", name=f"ao-{i + 1}")
            item.set_content(QLabel("Only clicking the arrow toggles this panel."))
            arrow_only.add_item(item)
        self.add_section(
            "Trigger Areas",
            "Only the arrow icon triggers expand/collapse (trigger_areas=['arrow']).",
            arrow_only,
        )

        # Custom title widget
        custom_title_collapse = TCollapse()
        item_custom = TCollapseItem(name="custom-title")
        title_btn = TButton(text="Custom Title Widget")
        item_custom.set_title(title_btn)
        item_custom.set_content(QLabel("Panel with a custom title widget instead of plain text."))
        custom_title_collapse.add_item(item_custom)
        self.add_section(
            "Custom Title",
            "Replace the default text title with a custom widget.",
            custom_title_collapse,
        )
