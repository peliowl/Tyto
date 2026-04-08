"""Disabled state mixin: 0.5 opacity via QSS + Forbidden cursor.

Uses QSS dynamic properties instead of QGraphicsOpacityEffect to avoid
rendering conflicts with QScrollArea viewports.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class DisabledMixin:
    """Mixin that applies 0.5 opacity via QSS and ForbiddenCursor when disabled.

    Call ``set_disabled_style(True)`` to enter the disabled visual state
    and ``set_disabled_style(False)`` to restore normal appearance.

    Opacity is controlled through a ``disabledState`` QSS dynamic property
    rather than ``QGraphicsOpacityEffect``, which causes rendering artefacts
    inside ``QScrollArea``.

    Designed for cooperative multiple inheritance with QWidget subclasses.

    Example:
        >>> class MyButton(BaseWidget, DisabledMixin):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self._init_disabled()
    """

    _disabled_original_cursor: Qt.CursorShape | None

    def _init_disabled(self: QWidget) -> None:  # type: ignore[misc]
        """Initialise disabled mixin resources. Call from __init__."""
        self._disabled_original_cursor = self.cursor().shape()

    def set_disabled_style(self, disabled: bool) -> None:
        """Apply or remove the disabled visual state.

        Args:
            disabled: True to enter disabled state, False to restore.
        """
        widget: QWidget = self  # type: ignore[assignment]

        if disabled:
            widget.setProperty("disabledState", True)
            widget.setCursor(Qt.CursorShape.ForbiddenCursor)
            widget.setEnabled(False)
        else:
            widget.setProperty("disabledState", False)
            original = getattr(self, "_disabled_original_cursor", Qt.CursorShape.ArrowCursor)
            widget.setCursor(original)
            widget.setEnabled(True)

        widget.style().unpolish(widget)
        widget.style().polish(widget)
