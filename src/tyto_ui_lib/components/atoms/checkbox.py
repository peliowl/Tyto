"""TCheckbox atom component: a three-state checkbox with animation.

Supports Checked, Unchecked, and Indeterminate states with smooth
transition animations and a state_changed signal.
"""

from __future__ import annotations

from enum import IntEnum

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


class _CheckIndicator(QWidget):
    """Internal widget that paints the check/indeterminate mark with animation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("checkbox_indicator")
        self.setFixedSize(QSize(16, 16))
        self._progress: float = 0.0
        self._state: int = 0  # 0=unchecked, 1=checked, 2=indeterminate

        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, value: float) -> None:
        self._progress = value
        self.update()

    progress = Property(float, _get_progress, _set_progress)  # type: ignore[assignment]

    def set_state(self, state: int) -> None:
        """Update the visual state with animation.

        Args:
            state: 0=unchecked, 1=checked, 2=indeterminate.
        """
        self._state = state
        target = 1.0 if state != 0 else 0.0
        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(target)
        self._anim.start()

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the checkmark or indeterminate dash based on current state."""
        if self._progress <= 0.01:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(Qt.GlobalColor.white)
        pen.setWidthF(2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        p = self._progress

        if self._state == 2:
            # Indeterminate: horizontal dash
            x1 = w * 0.25
            x2 = x1 + (w * 0.5) * p
            y = h / 2.0
            painter.drawLine(int(x1), int(y), int(x2), int(y))
        else:
            # Checkmark: two line segments
            ax, ay = w * 0.2, h * 0.5
            bx, by = w * 0.4, h * 0.75
            cx, cy = w * 0.8, h * 0.25

            if p <= 0.5:
                t = p * 2.0
                painter.drawLine(int(ax), int(ay), int(ax + (bx - ax) * t), int(ay + (by - ay) * t))
            else:
                painter.drawLine(int(ax), int(ay), int(bx), int(by))
                t = (p - 0.5) * 2.0
                painter.drawLine(int(bx), int(by), int(bx + (cx - bx) * t), int(by + (cy - by) * t))

        painter.end()


class TCheckbox(
    HoverEffectMixin,
    FocusGlowMixin,
    BaseWidget,
):
    """Checkbox component supporting three states: Checked, Unchecked, Indeterminate.

    Emits ``state_changed`` whenever the check state changes. Clicking
    toggles between Unchecked and Checked. The Indeterminate state can
    only be set programmatically.

    Args:
        label: Text label displayed next to the checkbox.
        state: Initial check state.
        parent: Optional parent widget.

    Signals:
        state_changed: Emitted with the new CheckState int value.

    Example:
        >>> cb = TCheckbox("Accept terms")
        >>> cb.state_changed.connect(lambda s: print(f"State: {s}"))
    """

    class CheckState(IntEnum):
        """Possible states for TCheckbox."""

        UNCHECKED = 0
        CHECKED = 1
        INDETERMINATE = 2

    state_changed = Signal(int)

    def __init__(
        self,
        label: str = "",
        state: CheckState = CheckState.UNCHECKED,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Initialise mixin resources
        self._init_hover_effect()
        self._init_focus_glow()

        self._state = state
        self._label_text = label

        # Layout: [indicator] [label]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

        self._indicator = _CheckIndicator(self)
        self._layout.addWidget(self._indicator)

        self._label = QLabel(label, self)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)
        self._layout.addStretch()

        # Dynamic property for QSS
        self.setProperty("checkState", self._state_name())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply initial state visuals (no animation)
        if state != self.CheckState.UNCHECKED:
            self._indicator._state = int(state)
            self._indicator._progress = 1.0

        self.apply_theme()

    # -- Public API --

    def get_state(self) -> CheckState:
        """Return the current check state.

        Returns:
            The current CheckState value.
        """
        return self._state

    def set_state(self, state: CheckState) -> None:
        """Set the check state programmatically.

        Args:
            state: The new CheckState to apply.
        """
        if state == self._state:
            return
        self._state = state
        self._indicator.set_state(int(state))
        self.setProperty("checkState", self._state_name())
        self.style().unpolish(self)
        self.style().polish(self)
        self.state_changed.emit(int(state))

    def toggle(self) -> None:
        """Toggle between Unchecked and Checked states."""
        if self._state == self.CheckState.CHECKED:
            self.set_state(self.CheckState.UNCHECKED)
        else:
            self.set_state(self.CheckState.CHECKED)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this checkbox."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("checkbox.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle click to toggle state."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(120, 24)

    # -- Private --

    def _state_name(self) -> str:
        """Return the QSS-friendly state name string."""
        names = {
            self.CheckState.UNCHECKED: "unchecked",
            self.CheckState.CHECKED: "checked",
            self.CheckState.INDETERMINATE: "indeterminate",
        }
        return names.get(self._state, "unchecked")
