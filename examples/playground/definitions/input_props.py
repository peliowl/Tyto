"""Property definitions for TInput in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TInput


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member."""
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def _apply_status(w: Any, v: Any) -> None:
    if not v or v == "":
        w.set_status(None)
    else:
        w.set_status(_to_enum(TInput.InputStatus, v))


def _apply_placeholder(w: Any, v: Any) -> None:
    text = str(v)
    if w._line_edit is not None:
        w._line_edit.setPlaceholderText(text)
    elif w._text_edit is not None:
        w._text_edit.setPlaceholderText(text)


def _apply_clearable(w: Any, v: Any) -> None:
    enabled = bool(v)
    w._clearable = enabled
    if w._clear_action is not None:
        if not enabled:
            w._clear_action.setVisible(False)
        elif w._line_edit and w._line_edit.text():
            w._clear_action.setVisible(True)


def _apply_maxlength(w: Any, v: Any) -> None:
    val = int(v) if v else 0
    w._maxlength = val if val > 0 else None
    if w._line_edit:
        w._line_edit.setMaxLength(val if val > 0 else 32767)


def _apply_show_count(w: Any, v: Any) -> None:
    w._show_count = bool(v)
    if bool(v):
        # Create count label if it doesn't exist
        if w._count_label is None:
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QLabel

            w._count_label = QLabel(w)
            w._count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            w._count_label.setObjectName("inputCountLabel")
            w._outer_layout.addWidget(w._count_label)
        w._count_label.setVisible(True)
        w._update_count_display()
    elif w._count_label is not None:
        w._count_label.setVisible(False)


def _apply_password(w: Any, v: Any) -> None:
    from PySide6.QtWidgets import QLineEdit

    enabled = bool(v)
    w._password = enabled
    if w._line_edit is not None:
        if enabled:
            w._line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            w._password_visible = False
        else:
            w._line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            w._password_visible = False


def _apply_input_type(w: Any, v: Any) -> None:
    """Recreate TInput with a different input type, carrying over properties."""
    it = _to_enum(TInput.InputType, v)
    parent_widget = w.parentWidget()
    if parent_widget is None:
        return
    parent_layout = parent_widget.layout()
    if parent_layout is None:
        return
    idx = parent_layout.indexOf(w)
    if idx < 0:
        return

    placeholder = "Enter text..."
    if w._line_edit:
        placeholder = w._line_edit.placeholderText() or placeholder
    elif w._text_edit:
        placeholder = w._text_edit.placeholderText() or placeholder

    new_w = TInput(
        placeholder=placeholder,
        input_type=it,
        clearable=w._clearable,
        maxlength=w._maxlength,
        show_count=w._show_count,
    )

    parent_layout.removeWidget(w)
    parent_layout.insertWidget(idx, new_w)

    # Update the preview's _current_widget reference via back-reference
    preview_owner = getattr(w, "_preview_owner", None)
    if preview_owner is not None:
        preview_owner._current_widget = new_w
        new_w._preview_owner = preview_owner

    w.setParent(None)
    w.deleteLater()


def register(registry: PropertyRegistry) -> None:
    """Register TInput property definitions and factory."""

    IS = TInput.InputSize
    ISt = TInput.InputStatus

    status_options: list[tuple[object, str]] = [
        ("", "none"),
        (ISt.SUCCESS.value, "success"),
        (ISt.WARNING.value, "warning"),
        (ISt.ERROR.value, "error"),
    ]

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="input_type", label="Type", prop_type="enum",
            default=TInput.InputType.TEXT.value,
            options=_enum_options(TInput.InputType),
            apply=_apply_input_type,
        ),
        PropertyDefinition(
            name="placeholder", label="Placeholder", prop_type="str",
            default="Enter text...",
            apply=_apply_placeholder,
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=IS.MEDIUM.value, options=_enum_options(IS),
            apply=lambda w, v: w.set_size(_to_enum(IS, v)),
        ),
        PropertyDefinition(
            name="clearable", label="Clearable", prop_type="bool", default=True,
            apply=_apply_clearable,
        ),
        PropertyDefinition(
            name="password", label="Password", prop_type="bool", default=False,
            apply=_apply_password,
        ),
        PropertyDefinition(
            name="round", label="Round", prop_type="bool", default=False,
            apply=lambda w, v: w.set_round(bool(v)),
        ),
        PropertyDefinition(
            name="bordered", label="Bordered", prop_type="bool", default=True,
            apply=lambda w, v: w.set_bordered(bool(v)),
        ),
        PropertyDefinition(
            name="maxlength", label="Max Length", prop_type="int", default=0,
            apply=_apply_maxlength,
        ),
        PropertyDefinition(
            name="show_count", label="Show Count", prop_type="bool", default=False,
            apply=_apply_show_count,
        ),
        PropertyDefinition(
            name="readonly", label="Readonly", prop_type="bool", default=False,
            apply=lambda w, v: w.set_readonly(bool(v)),
        ),
        PropertyDefinition(
            name="loading", label="Loading", prop_type="bool", default=False,
            apply=lambda w, v: w.set_loading(bool(v)),
        ),
        PropertyDefinition(
            name="status", label="Status", prop_type="enum",
            default="", options=status_options,
            apply=_apply_status,
        ),
    ]

    registry.register("input", definitions)
    registry.register_factory(
        "input", lambda: TInput(placeholder="Enter text...", clearable=True),
    )
