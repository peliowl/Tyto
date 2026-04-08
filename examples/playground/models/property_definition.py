"""Property definition dataclass for the playground property panel."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


@dataclass
class PropertyDefinition:
    """Metadata describing a single editable property of a component.

    Attributes:
        name: Internal property name, e.g. "button_type".
        label: Human-readable display label, e.g. "Type".
        prop_type: Property type – "enum", "bool", "str", "int", or "color".
        default: Default value for the property.
        options: List of ``(value, label)`` tuples for enum types.
        apply: Callable that applies the property value to a widget instance.
            Signature: ``(widget, value) -> None``.
    """

    name: str
    label: str
    prop_type: str  # "enum" | "bool" | "str" | "int" | "color"
    default: Any
    options: list[tuple[Any, str]] | None = None
    apply: Callable[[QWidget, Any], None] | None = field(default=None, repr=False)
