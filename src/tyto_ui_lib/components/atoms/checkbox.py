"""TCheckbox atom component: a three-state checkbox with animation.

Supports Checked, Unchecked, and Indeterminate states with smooth
transition animations, size variants, disabled state, and a
state_changed signal. TCheckboxGroup manages a collection of
TCheckbox instances with min/max selection constraints.
"""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import Any

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.disabled import DisabledMixin
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


# Indicator pixel sizes per CheckboxSize variant.
_INDICATOR_SIZES: dict[str, int] = {
    "small": 14,
    "medium": 16,
    "large": 20,
}

# Label font sizes per CheckboxSize variant.
_LABEL_FONT_SIZES: dict[str, int] = {
    "small": 12,
    "medium": 14,
    "large": 16,
}


def _lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
    """Linearly interpolate between two QColors.

    Args:
        c1: Start color.
        c2: End color.
        t: Interpolation factor in [0, 1].

    Returns:
        Interpolated QColor.
    """
    r = int(c1.red() + (c2.red() - c1.red()) * t)
    g = int(c1.green() + (c2.green() - c1.green()) * t)
    b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
    a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * t)
    return QColor(r, g, b, a)


class _CheckIndicator(QWidget):
    """Internal widget that paints the check/indeterminate mark with animation.

    Paints its own background, border, and checkmark/dash so that
    the visual state is always correct regardless of QSS rendering.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("checkbox_indicator")
        self.setFixedSize(QSize(16, 16))
        self._progress: float = 0.0
        self._state: int = 0  # 0=unchecked, 1=checked, 2=indeterminate

        # Theme-driven colors (set by TCheckbox._update_indicator_colors)
        self._bg_color = QColor("#ffffff")
        self._border_color = QColor("#e0e0e6")
        self._checked_color = QColor("#18a058")
        self._radius: int = 2

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

    def set_indicator_size(self, px: int) -> None:
        """Resize the indicator square.

        Args:
            px: Side length in pixels.
        """
        self.setFixedSize(QSize(px, px))

    def set_colors(
        self,
        bg_color: str,
        border_color: str,
        checked_color: str,
        radius: int,
    ) -> None:
        """Update the theme-driven colors used for painting.

        Args:
            bg_color: Background color for unchecked state.
            border_color: Border color for unchecked state.
            checked_color: Background and border color for checked/indeterminate state.
            radius: Border radius in pixels.
        """
        self._bg_color = QColor(bg_color)
        self._border_color = QColor(border_color)
        self._checked_color = QColor(checked_color)
        self._radius = radius
        self.update()

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint background, border, and checkmark/dash based on current state."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        p = self._progress

        # Interpolate background and border colors based on animation progress
        if p > 0.01:
            bg = _lerp_color(self._bg_color, self._checked_color, p)
            border = _lerp_color(self._border_color, self._checked_color, p)
        else:
            bg = self._bg_color
            border = self._border_color

        # Draw rounded-rect background
        painter.setPen(QPen(border, 2.0))
        painter.setBrush(QBrush(bg))
        painter.drawRoundedRect(1, 1, w - 2, h - 2, self._radius, self._radius)

        # Draw checkmark / indeterminate dash
        if p > 0.01:
            pen = QPen(QColor(Qt.GlobalColor.white))
            pen.setWidthF(2.0)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

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
    DisabledMixin,
    BaseWidget,
):
    """Checkbox component supporting three states with size variants and disabled state.

    Emits ``state_changed`` whenever the check state changes. Clicking
    toggles between Unchecked and Checked. The Indeterminate state can
    only be set programmatically.

    Args:
        label: Text label displayed next to the checkbox.
        state: Initial check state.
        size: Size variant (small / medium / large).
        disabled: Whether the checkbox starts disabled.
        value: Identifier value for use in TCheckboxGroup.
        focusable: Whether the checkbox can receive focus.
        checked_value: Custom value returned when checked.
        unchecked_value: Custom value returned when unchecked.
        default_checked: If True, start in CHECKED state (ignored if state is explicitly non-UNCHECKED).
        parent: Optional parent widget.

    Signals:
        state_changed: Emitted with the new CheckState int value.

    Example:
        >>> cb = TCheckbox("Accept terms", size=TCheckbox.CheckboxSize.SMALL)
        >>> cb.state_changed.connect(lambda s: print(f"State: {s}"))
    """

    class CheckState(IntEnum):
        """Possible states for TCheckbox."""

        UNCHECKED = 0
        CHECKED = 1
        INDETERMINATE = 2

    class CheckboxSize(str, Enum):
        """Size variants for TCheckbox."""

        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    state_changed = Signal(int)

    def __init__(
        self,
        label: str = "",
        state: CheckState = CheckState.UNCHECKED,
        size: CheckboxSize = CheckboxSize.MEDIUM,
        disabled: bool = False,
        value: Any = None,
        focusable: bool = True,
        checked_value: Any = True,
        unchecked_value: Any = False,
        default_checked: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Initialise mixin resources
        self._init_hover_effect()
        self._init_focus_glow()
        self._init_disabled()

        # Resolve initial state: explicit state takes precedence over default_checked
        if state == self.CheckState.UNCHECKED and default_checked:
            state = self.CheckState.CHECKED

        self._state = state
        self._label_text = label
        self._size = size
        self._disabled = disabled
        self._value = value
        self._checked_value = checked_value
        self._unchecked_value = unchecked_value

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

        # Dynamic properties for QSS
        self.setProperty("checkState", self._state_name())
        self.setProperty("checkboxSize", size.value)

        # Focusable
        if focusable:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply size variant
        self._apply_size()

        # Apply initial state visuals (no animation)
        if state != self.CheckState.UNCHECKED:
            self._indicator._state = int(state)
            self._indicator._progress = 1.0

        # Apply disabled after everything is set up
        if disabled:
            self.set_disabled(True)

        self.apply_theme()

    # -- Public properties --

    @property
    def size(self) -> CheckboxSize:
        """Return the current size variant."""
        return self._size

    @property
    def value(self) -> Any:
        """Return the identifier value for CheckboxGroup."""
        return self._value

    @property
    def checked_value(self) -> Any:
        """Return the custom value for checked state."""
        return self._checked_value

    @property
    def unchecked_value(self) -> Any:
        """Return the custom value for unchecked state."""
        return self._unchecked_value

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

    def get_value(self) -> Any:
        """Return checked_value or unchecked_value based on current state.

        Returns:
            checked_value if checked, unchecked_value otherwise.
        """
        if self._state == self.CheckState.CHECKED:
            return self._checked_value
        return self._unchecked_value

    def set_size(self, size: CheckboxSize) -> None:
        """Change the checkbox size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("checkboxSize", size.value)
        self._apply_size()
        self._repolish()

    def set_disabled(self, disabled: bool) -> None:
        """Enter or exit disabled state.

        Args:
            disabled: True to disable, False to enable.
        """
        self._disabled = disabled
        self.set_disabled_style(disabled)

    def is_disabled(self) -> bool:
        """Return whether the checkbox is currently disabled."""
        return self._disabled

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this checkbox and update indicator colors."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("checkbox.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)

            # Update indicator colors from current theme tokens
            self._update_indicator_colors()
            # Update label color from theme
            self._apply_size()
        except Exception:
            pass

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle click to toggle state. Blocked when disabled."""
        if self._disabled:
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:  # noqa: N802
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

    def _apply_size(self) -> None:
        """Apply indicator and label sizing for the current size variant."""
        indicator_px = _INDICATOR_SIZES.get(self._size.value, 16)
        font_px = _LABEL_FONT_SIZES.get(self._size.value, 14)
        self._indicator.set_indicator_size(indicator_px)

        # Include text color from theme so the inline stylesheet does not
        # override the inherited color (fixes dark-mode invisible text).
        engine = ThemeEngine.instance()
        text_color = ""
        if engine.current_theme():
            try:
                text_color = str(engine.get_token("colors", "text_primary"))
            except (RuntimeError, KeyError):
                pass
        if text_color:
            self._label.setStyleSheet(f"font-size: {font_px}px; color: {text_color};")
        else:
            self._label.setStyleSheet(f"font-size: {font_px}px;")

    def _update_indicator_colors(self) -> None:
        """Push current theme colors into the indicator for self-painting."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            bg = str(engine.get_token("colors", "bg_default"))
            border = str(engine.get_token("colors", "border"))
            primary = str(engine.get_token("colors", "primary"))
            radius = int(engine.get_token("radius", "small"))
        except (RuntimeError, KeyError):
            return
        self._indicator.set_colors(bg, border, primary, radius)

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()



class TCheckboxGroup(BaseWidget):
    """Checkbox group manager with min/max selection constraints.

    Manages a collection of TCheckbox instances, enforcing selection
    count limits and providing unified size/disabled control.

    Args:
        min: Minimum number of checkboxes that must be selected.
        max: Maximum number of checkboxes that can be selected (None = unlimited).
        size: Unified size for all child checkboxes (None = use each checkbox's own size).
        disabled: Whether all child checkboxes start disabled.
        default_value: List of checkbox values to pre-select.
        parent: Optional parent widget.

    Signals:
        value_changed: Emitted with list of selected checkbox values.

    Example:
        >>> group = TCheckboxGroup(min=1, max=3)
        >>> group.add_checkbox(TCheckbox("A", value="a"))
        >>> group.add_checkbox(TCheckbox("B", value="b"))
        >>> group.value_changed.connect(lambda v: print(f"Selected: {v}"))
    """

    value_changed = Signal(list)

    def __init__(
        self,
        min: int = 0,
        max: int | None = None,
        size: TCheckbox.CheckboxSize | None = None,
        disabled: bool = False,
        default_value: list[Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._min = min
        self._max = max
        self._group_size = size
        self._group_disabled = disabled
        self._checkboxes: list[TCheckbox] = []
        self._default_value = default_value or []

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

    # -- Public API --

    def add_checkbox(self, checkbox: TCheckbox) -> None:
        """Add a checkbox to the group.

        Applies group-level size and disabled settings, connects
        state_changed signal, and pre-selects if value is in default_value.

        Args:
            checkbox: The TCheckbox instance to add.
        """
        self._checkboxes.append(checkbox)
        self._layout.addWidget(checkbox)

        # Apply group-level overrides
        if self._group_size is not None:
            checkbox.set_size(self._group_size)
        if self._group_disabled:
            checkbox.set_disabled(True)

        # Pre-select if in default_value
        if checkbox.value in self._default_value and checkbox.get_state() != TCheckbox.CheckState.CHECKED:
            checkbox.set_state(TCheckbox.CheckState.CHECKED)

        # Connect state change with constraint enforcement
        checkbox.state_changed.connect(lambda _state, cb=checkbox: self._on_checkbox_changed(cb))

    def get_value(self) -> list[Any]:
        """Return list of values from all currently checked checkboxes.

        Returns:
            List of ``value`` attributes from checked TCheckbox instances.
        """
        return [cb.value for cb in self._checkboxes if cb.get_state() == TCheckbox.CheckState.CHECKED]

    def set_value(self, values: list[Any]) -> None:
        """Set which checkboxes are checked by their values.

        Checkboxes whose value is in *values* will be checked;
        all others will be unchecked. Min/max constraints are not
        enforced during programmatic set -- the caller is responsible.

        Args:
            values: List of values to check.
        """
        for cb in self._checkboxes:
            target = TCheckbox.CheckState.CHECKED if cb.value in values else TCheckbox.CheckState.UNCHECKED
            if cb.get_state() != target:
                cb.set_state(target)
        self.value_changed.emit(self.get_value())

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable all checkboxes in the group.

        Args:
            disabled: True to disable all, False to enable all.
        """
        self._group_disabled = disabled
        for cb in self._checkboxes:
            cb.set_disabled(disabled)

    def set_size(self, size: TCheckbox.CheckboxSize) -> None:
        """Set a unified size for all checkboxes in the group.

        Args:
            size: The size variant to apply.
        """
        self._group_size = size
        for cb in self._checkboxes:
            cb.set_size(size)

    # -- Private --

    def _on_checkbox_changed(self, checkbox: TCheckbox) -> None:
        """Handle a child checkbox state change with min/max enforcement."""
        checked_count = sum(1 for cb in self._checkboxes if cb.get_state() == TCheckbox.CheckState.CHECKED)

        # Enforce max constraint: revert check if over limit
        if self._max is not None and checked_count > self._max:
            checkbox.state_changed.disconnect()
            checkbox.set_state(TCheckbox.CheckState.UNCHECKED)
            checkbox.state_changed.connect(lambda _state, cb=checkbox: self._on_checkbox_changed(cb))
            return

        # Enforce min constraint: revert uncheck if under limit
        if checked_count < self._min and checkbox.get_state() == TCheckbox.CheckState.UNCHECKED:
            checkbox.state_changed.disconnect()
            checkbox.set_state(TCheckbox.CheckState.CHECKED)
            checkbox.state_changed.connect(lambda _state, cb=checkbox: self._on_checkbox_changed(cb))
            return

        self.value_changed.emit(self.get_value())
