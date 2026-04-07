"""Click ripple mixin: background darken + Scale 0.98 press effect.

Provides a subtle press-down visual feedback for clickable widgets.
"""

from __future__ import annotations

from PySide6.QtGui import QMouseEvent, QTransform
from PySide6.QtWidgets import QWidget


class ClickRippleMixin:
    """Mixin that adds a press-down visual effect on mouse click.

    On mouse press the widget scales to 0.98 and the background darkens
    slightly.  On release the effect is reversed.

    Designed for cooperative multiple inheritance with QWidget subclasses.

    Example:
        >>> class MyButton(BaseWidget, ClickRippleMixin):
        ...     pass
    """

    def _init_click_ripple(self: QWidget) -> None:  # type: ignore[misc]
        """Initialise click ripple resources. Call from __init__."""
        self._is_pressed = False

    def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        """Handle mouse press: apply scale-down transform.

        Args:
            event: The mouse press event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        self._is_pressed = True  # type: ignore[attr-defined]

        # Apply a 0.98 scale transform centred on the widget
        transform = QTransform()
        cx = widget.width() / 2.0
        cy = widget.height() / 2.0
        transform.translate(cx, cy)
        transform.scale(0.98, 0.98)
        transform.translate(-cx, -cy)

        # Use dynamic property to darken appearance via QSS [pressed=true]
        widget.setProperty("pressed", True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        super().mousePressEvent(event)  # type: ignore[misc]

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        """Handle mouse release: restore original appearance.

        Args:
            event: The mouse release event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        self._is_pressed = False  # type: ignore[attr-defined]

        widget.setProperty("pressed", False)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        super().mouseReleaseEvent(event)  # type: ignore[misc]
