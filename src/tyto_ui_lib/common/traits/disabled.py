"""Disabled state mixin: 0.5 opacity + Forbidden cursor.

Provides a consistent disabled visual treatment for any widget.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


class DisabledMixin:
    """Mixin that applies 0.5 opacity and ForbiddenCursor when disabled.

    Call ``set_disabled_style(True)`` to enter the disabled visual state
    and ``set_disabled_style(False)`` to restore normal appearance.

    Designed for cooperative multiple inheritance with QWidget subclasses.

    Example:
        >>> class MyButton(BaseWidget, DisabledMixin):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self._init_disabled()
    """

    _disabled_opacity_effect: QGraphicsOpacityEffect | None
    _disabled_original_cursor: Qt.CursorShape | None

    def _init_disabled(self: QWidget) -> None:  # type: ignore[misc]
        """Initialise disabled mixin resources. Call from __init__."""
        self._disabled_original_cursor = self.cursor().shape()
        self._disabled_opacity_effect = QGraphicsOpacityEffect(self)
        self._disabled_opacity_effect.setOpacity(1.0)

    def set_disabled_style(self, disabled: bool) -> None:
        """Apply or remove the disabled visual state.

        Args:
            disabled: True to enter disabled state, False to restore.
        """
        widget: QWidget = self  # type: ignore[assignment]

        if disabled:
            if hasattr(self, "_disabled_opacity_effect") and self._disabled_opacity_effect is not None:
                self._disabled_opacity_effect.setOpacity(0.5)
                widget.setGraphicsEffect(self._disabled_opacity_effect)
            widget.setCursor(Qt.CursorShape.ForbiddenCursor)
            widget.setEnabled(False)
        else:
            if hasattr(self, "_disabled_opacity_effect") and self._disabled_opacity_effect is not None:
                self._disabled_opacity_effect.setOpacity(1.0)
                widget.setGraphicsEffect(self._disabled_opacity_effect)
            original = getattr(self, "_disabled_original_cursor", Qt.CursorShape.ArrowCursor)
            widget.setCursor(original)
            widget.setEnabled(True)
