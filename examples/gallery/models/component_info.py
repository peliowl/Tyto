"""Component metadata dataclass for the gallery registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


@dataclass
class ComponentInfo:
    """Metadata describing a single gallery component.

    Attributes:
        name: Human-readable display name, e.g. "Button".
        key: Unique identifier in kebab-case, e.g. "button".
        category: Classification tier – "atoms", "molecules", or "organisms".
        showcase_factory: Callable that creates the showcase widget for this
            component.  Receives an optional parent ``QWidget``.
    """

    name: str
    key: str
    category: str
    showcase_factory: Callable[..., QWidget]
