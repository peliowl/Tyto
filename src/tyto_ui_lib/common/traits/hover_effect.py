"""Hover effect mixin: PointingHand cursor + QSS dynamic property for hover styling.

Uses QSS dynamic properties instead of QGraphicsEffect to avoid rendering
conflicts with QScrollArea viewports.  The actual hover colour transition
is driven by QSS ``:hover`` pseudo-state rules defined in each component's
``.qss.j2`` template.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QWidget


class HoverEffectMixin:
    """Mixin that sets a PointingHand cursor on hover and toggles a ``hovered``
    QSS dynamic property.

    Hover colour transitions are handled entirely by QSS ``:hover``
    pseudo-state selectors in each component's template, avoiding
    ``QGraphicsEffect`` which causes rendering artefacts inside
    ``QScrollArea``.

    This mixin is designed for cooperative multiple inheritance with QWidget
    subclasses.  It calls ``super()`` in every event handler to ensure the
    MRO chain is preserved.

    Example:
        >>> class MyButton(BaseWidget, HoverEffectMixin):
        ...     pass
    """

    _original_cursor: Qt.CursorShape | None

    def _init_hover_effect(self: QWidget) -> None:  # type: ignore[misc]
        """Initialise hover effect resources. Call from __init__."""
        self._original_cursor = self.cursor().shape()

    def enterEvent(self, event: QEnterEvent) -> None:  # type: ignore[override]
        """Handle mouse enter: change cursor to PointingHand and set hovered property.

        Args:
            event: The enter event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        widget.setCursor(Qt.CursorShape.PointingHandCursor)

        widget.setProperty("hovered", True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        super().enterEvent(event)  # type: ignore[misc]

    def leaveEvent(self, event: QEvent) -> None:  # type: ignore[override]
        """Handle mouse leave: restore cursor and clear hovered property.

        Args:
            event: The leave event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        original = getattr(self, "_original_cursor", Qt.CursorShape.ArrowCursor)
        widget.setCursor(original)

        widget.setProperty("hovered", False)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        super().leaveEvent(event)  # type: ignore[misc]
