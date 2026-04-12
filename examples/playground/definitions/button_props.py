"""Property definitions for TButton in the Playground."""

from __future__ import annotations

from enum import Enum
from typing import Any

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TButton


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum.

    Stores the string *value* (not the enum member) as item data so that
    QComboBox.itemData() always returns a plain str.
    """
    return [(m.value, m.value) for m in enum_cls]


def _to_enum(enum_cls: type[Enum], v: Any) -> Enum:
    """Convert a raw value back to an enum member.

    QComboBox itemData returns plain str for str-enums, so we need
    to reconstruct the enum member from its value.
    """
    if isinstance(v, enum_cls):
        return v
    return enum_cls(v)


def _apply_button_type(w: Any, v: Any) -> None:
    """Apply button type change, converting str back to enum."""
    bt = _to_enum(TButton.ButtonType, v)
    w.set_button_type(bt)


def _apply_icon(w: Any, v: Any) -> None:
    """Apply icon from a file path, or clear if empty."""
    from PySide6.QtGui import QIcon

    path = str(v) if v else ""
    if path:
        w.set_icon(QIcon(path), w._icon_placement)
    else:
        w.set_icon(None, w._icon_placement)


def register(registry: PropertyRegistry) -> None:
    """Register TButton property definitions and factory."""

    BT = TButton.ButtonType
    BS = TButton.ButtonSize

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="text", label="Text", prop_type="str", default="Button",
            apply=lambda w, v: w.set_text(str(v)),
        ),
        PropertyDefinition(
            name="button_type", label="Type", prop_type="enum",
            default=BT.DEFAULT.value, options=_enum_options(BT),
            apply=_apply_button_type,
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=BS.MEDIUM.value, options=_enum_options(BS),
            apply=lambda w, v: w.set_size(_to_enum(BS, v)),
        ),
        PropertyDefinition(
            name="loading", label="Loading", prop_type="bool", default=False,
            apply=lambda w, v: w.set_loading(bool(v)),
        ),
        PropertyDefinition(
            name="disabled", label="Disabled", prop_type="bool", default=False,
            apply=lambda w, v: w.set_disabled(bool(v)),
        ),
        PropertyDefinition(
            name="circle", label="Circle", prop_type="bool", default=False,
            apply=lambda w, v: w.set_circle(bool(v)),
        ),
        PropertyDefinition(
            name="round", label="Round", prop_type="bool", default=False,
            apply=lambda w, v: w.set_round(bool(v)),
        ),
        PropertyDefinition(
            name="ghost", label="Ghost", prop_type="bool", default=False,
            apply=lambda w, v: w.set_ghost(bool(v)),
        ),
        PropertyDefinition(
            name="strong", label="Strong", prop_type="bool", default=False,
            apply=lambda w, v: w.set_strong(bool(v)),
        ),
        PropertyDefinition(
            name="block", label="Block", prop_type="bool", default=False,
            apply=lambda w, v: w.set_block(bool(v)),
        ),
        PropertyDefinition(
            name="bordered", label="Bordered", prop_type="bool", default=True,
            apply=lambda w, v: w.set_bordered(bool(v)),
        ),
        PropertyDefinition(
            name="color", label="Color", prop_type="color", default="",
            apply=lambda w, v: w.set_color(str(v) if v else None),
        ),
        PropertyDefinition(
            name="text_color", label="Text Color", prop_type="color", default="",
            apply=lambda w, v: w.set_text_color(str(v) if v else None),
        ),
        PropertyDefinition(
            name="icon", label="Icon", prop_type="file", default="",
            apply=_apply_icon,
        ),
        PropertyDefinition(
            name="icon_placement", label="Icon Placement", prop_type="enum",
            default=TButton.IconPlacement.LEFT.value,
            options=_enum_options(TButton.IconPlacement),
            apply=lambda w, v: w.set_icon(
                w._icon, _to_enum(TButton.IconPlacement, v),
            ),
        ),
    ]

    registry.register("button", definitions)
    registry.register_factory("button", lambda: TButton(text="Button"))
