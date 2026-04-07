"""Hover effect mixin: 200ms background color transition + PointingHand cursor.

Applies a smooth hover visual feedback to any QWidget subclass.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QEnterEvent
from PySide6.QtWidgets import QGraphicsColorizeEffect, QWidget
from shiboken6 import isValid as _is_valid  # type: ignore[import-untyped]

from tyto_ui_lib.core.theme_engine import ThemeEngine


class HoverEffectMixin:
    """Mixin that adds a 200ms background-color hover transition and PointingHand cursor.

    When the mouse enters the widget, the cursor changes to PointingHand and
    a subtle colorize effect is applied with a 200ms animation.  On leave the
    effect is reversed.

    This mixin is designed for cooperative multiple inheritance with QWidget
    subclasses.  It calls ``super()`` in every event handler to ensure the
    MRO chain is preserved.

    Example:
        >>> class MyButton(BaseWidget, HoverEffectMixin):
        ...     pass
    """

    _hover_animation: QPropertyAnimation | None
    _hover_effect: QGraphicsColorizeEffect | None
    _original_cursor: Qt.CursorShape | None

    def _init_hover_effect(self: QWidget) -> None:  # type: ignore[misc]
        """Initialise hover effect resources. Call from __init__."""
        self._original_cursor = self.cursor().shape()
        self._hover_effect = QGraphicsColorizeEffect(self)
        self._hover_effect.setColor(QColor(0, 0, 0, 0))
        self._hover_effect.setStrength(0.0)
        self.setGraphicsEffect(self._hover_effect)

        self._hover_animation = QPropertyAnimation(self._hover_effect, b"strength", self)
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def enterEvent(self, event: QEnterEvent) -> None:  # type: ignore[override]
        """Handle mouse enter: start hover-in animation and change cursor.

        Args:
            event: The enter event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        widget.setCursor(Qt.CursorShape.PointingHandCursor)

        if (
            hasattr(self, "_hover_animation")
            and self._hover_animation is not None
            and self._hover_effect is not None
            and _is_valid(self._hover_effect)
            and _is_valid(self._hover_animation)
        ):
            engine = ThemeEngine.instance()
            try:
                hover_color = engine.get_token("colors", "primary_hover")
                if isinstance(hover_color, str):
                    self._hover_effect.setColor(QColor(hover_color))
            except (RuntimeError, KeyError):
                try:
                    self._hover_effect.setColor(QColor(0, 0, 0, 30))
                except RuntimeError:
                    pass

            self._hover_animation.stop()
            self._hover_animation.setStartValue(0.0)
            self._hover_animation.setEndValue(0.15)
            self._hover_animation.start()

        super().enterEvent(event)  # type: ignore[misc]

    def leaveEvent(self, event: QEvent) -> None:  # type: ignore[override]
        """Handle mouse leave: reverse hover animation and restore cursor.

        Args:
            event: The leave event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        original = getattr(self, "_original_cursor", Qt.CursorShape.ArrowCursor)
        widget.setCursor(original)

        if (
            hasattr(self, "_hover_animation")
            and self._hover_animation is not None
            and self._hover_effect is not None
            and _is_valid(self._hover_effect)
            and _is_valid(self._hover_animation)
        ):
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_effect.strength())
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()

        super().leaveEvent(event)  # type: ignore[misc]
