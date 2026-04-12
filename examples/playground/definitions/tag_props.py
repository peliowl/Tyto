"""Property definitions for TTag in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TTag


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def _apply_tag_type(w: Any, v: Any) -> None:
    """Apply tag type change, converting str back to enum."""
    tt = _to_enum(TTag.TagType, v)
    w.set_tag_type(tt)


def _apply_tag_size(w: Any, v: Any) -> None:
    """Apply tag size change, converting str back to enum."""
    ts = _to_enum(TTag.TagSize, v)
    w.set_size(ts)


def _apply_closable(w: Any, v: Any) -> None:
    """Toggle the close button on/off at runtime."""
    from PySide6.QtCore import QSize, Qt
    from PySide6.QtWidgets import QPushButton

    enabled = bool(v)
    w._closable = enabled
    if enabled and w._close_btn is None:
        w._close_btn = QPushButton("\u2715", w)
        w._close_btn.setObjectName("tag_close_btn")
        w._close_btn.setFixedSize(QSize(16, 16))
        w._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        w._close_btn.clicked.connect(w._on_close_clicked)
        w._layout.addWidget(w._close_btn)
    elif not enabled and w._close_btn is not None:
        w._close_btn.setVisible(False)
    elif enabled and w._close_btn is not None:
        w._close_btn.setVisible(True)


def _apply_checkable(w: Any, v: Any) -> None:
    """Toggle checkable mode at runtime."""
    w.set_checkable(bool(v))


def register(registry: PropertyRegistry) -> None:
    """Register TTag property definitions and factory."""

    TT = TTag.TagType
    TS = TTag.TagSize

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="text", label="Text", prop_type="str", default="Tag",
            apply=lambda w, v: w.set_text(str(v)),
        ),
        PropertyDefinition(
            name="tag_type", label="Type", prop_type="enum",
            default=TT.DEFAULT.value, options=_enum_options(TT),
            apply=_apply_tag_type,
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=TS.MEDIUM.value, options=_enum_options(TS),
            apply=_apply_tag_size,
        ),
        PropertyDefinition(
            name="closable", label="Closable", prop_type="bool", default=False,
            apply=_apply_closable,
        ),
        PropertyDefinition(
            name="round", label="Round", prop_type="bool", default=False,
            apply=lambda w, v: w.set_round(bool(v)),
        ),
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.set_disabled(bool(v)),
        ),
        PropertyDefinition(
            name="bordered", label="Bordered", prop_type="bool", default=True,
            apply=lambda w, v: w.set_bordered(bool(v)),
        ),
        PropertyDefinition(
            name="checkable", label="Checkable", prop_type="bool", default=False,
            apply=_apply_checkable,
        ),
        PropertyDefinition(
            name="strong", label="Strong", prop_type="bool", default=False,
            apply=lambda w, v: w.set_strong(bool(v)),
        ),
    ]

    registry.register("tag", definitions)
    registry.register_factory("tag", lambda: TTag(text="Tag"))
