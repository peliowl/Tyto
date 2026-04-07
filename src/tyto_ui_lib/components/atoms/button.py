"""TButton atom component: a versatile button with four visual types.

Supports Primary, Default, Dashed, and Text types with loading and
disabled states.  Mixes in HoverEffect, ClickRipple, FocusGlow, and
Disabled behaviors for rich interaction feedback.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.click_ripple import ClickRippleMixin
from tyto_ui_lib.common.traits.disabled import DisabledMixin
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine

# Simple circular-arc SVG used as the loading spinner icon.
_SPINNER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
    '<circle cx="8" cy="8" r="6" fill="none" stroke="currentColor"'
    ' stroke-width="2" stroke-dasharray="28 10" stroke-linecap="round"/>'
    "</svg>"
)


class _SpinnerWidget(QWidget):
    """Internal widget that renders a rotating SVG spinner."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._renderer = QSvgRenderer(_SPINNER_SVG.encode(), self)
        self._angle: float = 0.0
        self.setFixedSize(QSize(16, 16))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._anim = QPropertyAnimation(self, b"angle", self)
        self._anim.setDuration(1000)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(360.0)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)

    def _get_angle(self) -> float:
        return self._angle

    def _set_angle(self, value: float) -> None:
        self._angle = value
        self.update()

    angle = Property(float, _get_angle, _set_angle)  # type: ignore[assignment]

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Render the SVG spinner rotated by the current angle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        painter.rotate(self._angle)
        painter.translate(-self.width() / 2.0, -self.height() / 2.0)
        self._renderer.render(painter, self.rect().toRectF())
        painter.end()

    def start(self) -> None:
        """Start the rotation animation."""
        self._anim.start()

    def stop(self) -> None:
        """Stop the rotation animation."""
        self._anim.stop()


class TButton(
    HoverEffectMixin,
    ClickRippleMixin,
    FocusGlowMixin,
    DisabledMixin,
    BaseWidget,
):
    """Button component supporting Primary, Default, Dashed, and Text types.

    Emits ``clicked`` on mouse release when not loading or disabled.
    Provides a loading state with an animated SVG spinner that blocks
    all click events.

    Args:
        text: Button label text.
        button_type: Visual type (Primary, Default, Dashed, Text).
        loading: Whether the button starts in loading state.
        disabled: Whether the button starts disabled.
        parent: Optional parent widget.

    Signals:
        clicked: Emitted when the button is clicked (not loading, not disabled).

    Example:
        >>> btn = TButton("Submit", button_type=TButton.ButtonType.PRIMARY)
        >>> btn.clicked.connect(lambda: print("clicked"))
    """

    class ButtonType(str, Enum):
        """Visual type variants for TButton."""

        PRIMARY = "primary"
        DEFAULT = "default"
        DASHED = "dashed"
        TEXT = "text"

    clicked = Signal()

    def __init__(
        self,
        text: str = "",
        button_type: ButtonType = ButtonType.DEFAULT,
        loading: bool = False,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Initialise mixin resources
        self._init_hover_effect()
        self._init_click_ripple()
        self._init_focus_glow()
        self._init_disabled()

        self._button_type = button_type
        self._loading = False
        self._text = text

        # Layout: [spinner] [label]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spinner = _SpinnerWidget(self)
        self._spinner.setVisible(False)
        self._layout.addWidget(self._spinner)

        self._label = QLabel(text, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)

        # Apply dynamic property for QSS selectors
        self.setProperty("buttonType", button_type.value)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply initial states
        if loading:
            self.set_loading(True)
        if disabled:
            self.set_disabled(True)

        self.apply_theme()

    # -- Public API --

    @property
    def button_type(self) -> ButtonType:
        """Return the current button type."""
        return self._button_type

    @property
    def loading(self) -> bool:
        """Return whether the button is in loading state."""
        return self._loading

    @property
    def text(self) -> str:
        """Return the button label text."""
        return self._text

    def set_text(self, text: str) -> None:
        """Update the button label text.

        Args:
            text: New label string.
        """
        self._text = text
        self._label.setText(text)

    def set_loading(self, loading: bool) -> None:
        """Enter or exit loading state.

        In loading state the spinner is shown and all clicks are blocked.

        Args:
            loading: True to enter loading state, False to exit.
        """
        self._loading = loading
        self._spinner.setVisible(loading)
        if loading:
            self._spinner.start()
            self.setCursor(Qt.CursorShape.WaitCursor)
        else:
            self._spinner.stop()
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_disabled(self, disabled: bool) -> None:
        """Enter or exit disabled state via DisabledMixin.

        Args:
            disabled: True to disable, False to enable.
        """
        self.set_disabled_style(disabled)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this button."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("button.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    # -- Event overrides --

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Block press events when loading; otherwise delegate to mixins."""
        if self._loading:
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Emit ``clicked`` on release when not loading/disabled."""
        if self._loading:
            event.accept()
            return
        super().mouseReleaseEvent(event)
        if self.isEnabled() and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(80, 34)
