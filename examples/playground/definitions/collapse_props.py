"""Property definitions for TCollapse in the Playground."""

from __future__ import annotations

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QPushButton

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TCollapse, TCollapseItem


def _make_collapse() -> TCollapse:
    """Create a default TCollapse with sample items and content."""
    c = TCollapse()
    for i in range(3):
        item = TCollapseItem(title=f"Panel {i + 1}", name=f"panel-{i + 1}")
        content = QLabel(f"This is the content of panel {i + 1}.\nIt can contain multiple lines.")
        content.setWordWrap(True)
        item.set_content(content)
        c.add_item(item)
    return c


def _apply_trigger_areas(w: TCollapse, v: str) -> None:  # type: ignore[type-arg]
    """Apply trigger areas from a preset string."""
    mapping: dict[str, list[str]] = {
        "main": ["main"],
        "arrow": ["arrow"],
        "extra": ["extra"],
        "main+arrow": ["main", "arrow"],
        "main+extra": ["main", "extra"],
        "all": ["main", "extra", "arrow"],
    }
    w.trigger_areas = mapping.get(str(v), ["main"])


def _apply_custom_title(w: TCollapse, v: str) -> None:  # type: ignore[type-arg]
    """Set custom title text on the first panel via input field."""
    if w.items:
        item = w.items[0]
        text = str(v).strip()
        if text:
            title_label = QLabel(text)
            item.set_title(title_label)
        else:
            item.title = "Panel 1"


def _apply_header_extra(w: TCollapse, v: bool) -> None:  # type: ignore[type-arg]
    """Toggle header extra widget on the first panel."""
    if w.items:
        item = w.items[0]
        if v:
            btn = QPushButton("Extra")
            btn.setFixedHeight(22)
            item.set_header_extra(btn)
        else:
            item.set_header_extra(QLabel(""))


# Preset arrow icons: Unicode symbols
_ARROW_PRESETS: dict[str, str] = {
    "default": "",
    "\u25b6 Triangle": "\u25b6",
    "\u2605 Star": "\u2605",
    "\u2795 Plus": "\u2795",
    "\u2714 Check": "\u2714",
    "\u25cf Circle": "\u25cf",
    "\u2666 Diamond": "\u2666",
}


def _apply_arrow_preset(w: TCollapse, v: str) -> None:  # type: ignore[type-arg]
    """Apply a preset arrow icon on the first panel."""
    if w.items:
        item = w.items[0]
        symbol = _ARROW_PRESETS.get(str(v), "")
        if symbol:
            arrow = QLabel(symbol)
            item.set_arrow(arrow)
        else:
            # Reset to default arrow
            item.set_arrow(QLabel(""))
            item._update_arrow()


def _apply_arrow_file(w: TCollapse, v: str) -> None:  # type: ignore[type-arg]
    """Apply a custom arrow icon from file path on the first panel."""
    if w.items:
        item = w.items[0]
        path = str(v).strip()
        if path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                arrow = QLabel()
                arrow.setPixmap(pixmap.scaled(16, 16))
                item.set_arrow(arrow)
        else:
            item.set_arrow(QLabel(""))
            item._update_arrow()


def register(registry: PropertyRegistry) -> None:
    """Register TCollapse property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="accordion", label="Accordion", prop_type="bool", default=False,
            apply=lambda w, v: setattr(w, "accordion", bool(v)),
        ),
        PropertyDefinition(
            name="arrow_placement", label="Arrow Placement", prop_type="enum",
            default="left", options=[("left", "left"), ("right", "right")],
            apply=lambda w, v: setattr(w, "arrow_placement", str(v)),
        ),
        PropertyDefinition(
            name="trigger_areas", label="Trigger Areas", prop_type="enum",
            default="main",
            options=[
                ("main", "main"),
                ("arrow", "arrow"),
                ("extra", "extra"),
                ("main+arrow", "main+arrow"),
                ("main+extra", "main+extra"),
                ("all", "all"),
            ],
            apply=lambda w, v: _apply_trigger_areas(w, v),
        ),
        PropertyDefinition(
            name="custom_title", label="Custom Title (Panel 1)", prop_type="str", default="",
            apply=lambda w, v: _apply_custom_title(w, str(v)),
        ),
        PropertyDefinition(
            name="header_extra", label="Header Extra (Panel 1)", prop_type="bool", default=False,
            apply=lambda w, v: _apply_header_extra(w, bool(v)),
        ),
        PropertyDefinition(
            name="arrow_preset", label="Arrow Icon (Panel 1)", prop_type="enum",
            default="default",
            options=[
                ("default", "Default"),
                ("\u25b6 Triangle", "\u25b6 Triangle"),
                ("\u2605 Star", "\u2605 Star"),
                ("\u2795 Plus", "\u2795 Plus"),
                ("\u2714 Check", "\u2714 Check"),
                ("\u25cf Circle", "\u25cf Circle"),
                ("\u2666 Diamond", "\u2666 Diamond"),
            ],
            apply=lambda w, v: _apply_arrow_preset(w, v),
        ),
        PropertyDefinition(
            name="arrow_file", label="Arrow Icon File (Panel 1)", prop_type="file", default="",
            apply=lambda w, v: _apply_arrow_file(w, str(v)),
        ),
    ]

    registry.register("collapse", definitions)
    registry.register_factory("collapse", _make_collapse)
