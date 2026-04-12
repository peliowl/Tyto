"""Property definitions for TPopconfirm in the Playground."""

from __future__ import annotations

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TButton, TPopconfirm


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def register(registry: PropertyRegistry) -> None:
    """Register TPopconfirm property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="title", label="Title", prop_type="str", default="\u786e\u8ba4\u64cd\u4f5c\uff1f",
            apply=lambda w, v: setattr(w, "title", str(v)),
        ),
        PropertyDefinition(
            name="confirm_text", label="Confirm Text", prop_type="str", default="\u786e\u8ba4",
            apply=lambda w, v: setattr(w, "confirm_text", str(v)),
        ),
        PropertyDefinition(
            name="cancel_text", label="Cancel Text", prop_type="str", default="\u53d6\u6d88",
            apply=lambda w, v: setattr(w, "cancel_text", str(v)),
        ),
        PropertyDefinition(
            name="placement", label="Placement", prop_type="enum",
            default=TPopconfirm.Placement.TOP.value,
            options=_enum_options(TPopconfirm.Placement),
            apply=lambda w, v: setattr(w, "placement", TPopconfirm.Placement(v)),
        ),
        PropertyDefinition(
            name="trigger_mode", label="Trigger Mode", prop_type="enum",
            default=TPopconfirm.TriggerMode.CLICK.value,
            options=_enum_options(TPopconfirm.TriggerMode),
            apply=lambda w, v: setattr(w, "trigger_mode", v),
        ),
        PropertyDefinition(
            name="show_icon", label="Show Icon", prop_type="bool", default=True,
            apply=lambda w, v: setattr(w, "show_icon", bool(v)),
        ),
    ]

    registry.register("popconfirm", definitions)
    registry.register_factory(
        "popconfirm",
        lambda: TPopconfirm(trigger=TButton(text="Click me"), title="\u786e\u8ba4\u64cd\u4f5c\uff1f"),
    )
