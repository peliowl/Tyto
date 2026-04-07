"""Focus glow mixin: 2px semi-transparent primary color glow on focus.

Provides a focus ring visual feedback for keyboard-navigable widgets.
"""

from __future__ import annotations

from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import QWidget


class FocusGlowMixin:
    """Mixin that adds a 2px semi-transparent primary-color glow on focus.

    When the widget gains keyboard focus a ``focused`` dynamic property is
    set to ``True``, enabling QSS rules like ``[focused=true]`` to render
    a glow border.  The property is cleared on focus-out.

    Designed for cooperative multiple inheritance with QWidget subclasses.

    Example:
        >>> class MyInput(BaseWidget, FocusGlowMixin):
        ...     pass
    """

    def _init_focus_glow(self: QWidget) -> None:  # type: ignore[misc]
        """Initialise focus glow resources. Call from __init__."""
        self._is_focused = False

    def focusInEvent(self, event: QFocusEvent) -> None:  # type: ignore[override]
        """Handle focus-in: apply glow effect via dynamic property.

        Args:
            event: The focus event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        self._is_focused = True  # type: ignore[attr-defined]

        widget.setProperty("focused", True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        super().focusInEvent(event)  # type: ignore[misc]

    def focusOutEvent(self, event: QFocusEvent) -> None:  # type: ignore[override]
        """Handle focus-out: remove glow effect.

        Args:
            event: The focus event.
        """
        widget: QWidget = self  # type: ignore[assignment]
        self._is_focused = False  # type: ignore[attr-defined]

        widget.setProperty("focused", False)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

        super().focusOutEvent(event)  # type: ignore[misc]
