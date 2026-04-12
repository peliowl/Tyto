"""TInputNumber: numeric input with step control, range limits, and precision.

Provides a numeric input field with +/- buttons, keyboard arrow key support,
long-press continuous increment/decrement, input validation, loading state,
clearable, status variants, custom formatting, and more.
"""

from __future__ import annotations

import builtins
from collections.abc import Callable
from enum import Enum
from typing import Any

from PySide6.QtCore import QRectF, QSize, QTimer, Property, Signal, Qt
from PySide6.QtGui import (
    QColor,
    QDoubleValidator,
    QFont,
    QIcon,
    QIntValidator,
    QKeyEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color


def _clamp(value: float, lo: float | None, hi: float | None) -> float:
    """Clamp *value* to [lo, hi], treating None as unbounded."""
    if lo is not None and value < lo:
        return lo
    if hi is not None and value > hi:
        return hi
    return value


def _round_to_precision(value: float, precision: int) -> float:
    """Round *value* to the given decimal precision."""
    if precision <= 0:
        return float(round(value))
    return round(value, precision)


def _to_svg_color(color: str) -> str:
    """Convert a CSS color string to an SVG-safe color string.

    SVG fill/stroke attributes don't support CSS rgba() syntax.
    Converts through QColor to produce rgb(r,g,b) format.
    """
    c = QColor(color.strip())
    if c.isValid():
        return f"rgb({c.red()},{c.green()},{c.blue()})"
    return color.strip()


def _text_icon(char: str, size: int = 20, color: QColor | None = None) -> QIcon:
    """Create a QIcon by rendering a single Unicode character onto a pixmap."""
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    if color is not None:
        painter.setPen(color)
    else:
        painter.setPen(QColor("#667085"))
    font = QFont()
    font.setPixelSize(int(size * 0.75))
    painter.setFont(font)
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, char)
    painter.end()
    return QIcon(px)


class _SpinnerWidget(QWidget):
    """Internal rotating SVG spinner for loading state."""

    def __init__(self, parent: QWidget | None = None, color: str = "#667085") -> None:
        super().__init__(parent)
        from PySide6.QtCore import QEasingCurve, QPropertyAnimation
        from PySide6.QtSvg import QSvgRenderer

        self._color = color
        svg = self._build_svg(color)
        self._renderer = QSvgRenderer(svg, self)
        self._angle: float = 0.0
        self.setFixedSize(QSize(16, 16))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._anim = QPropertyAnimation(self, b"angle", self)
        self._anim.setDuration(1000)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(360.0)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)

    @staticmethod
    def _build_svg(color: str) -> bytes:
        c = _to_svg_color(color)
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
            f'<circle cx="8" cy="8" r="6" fill="none" stroke="{c}"'
            ' stroke-width="2" stroke-dasharray="28 10" stroke-linecap="round"/>'
            "</svg>"
        ).encode()

    def set_color(self, color: str) -> None:
        self._color = color
        self._renderer.load(self._build_svg(color))
        self.update()

    def _get_angle(self) -> float:
        return self._angle

    def _set_angle(self, value: float) -> None:
        self._angle = value
        self.update()

    angle = Property(float, _get_angle, _set_angle)  # type: ignore[assignment]

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        painter.rotate(self._angle)
        painter.translate(-self.width() / 2.0, -self.height() / 2.0)
        self._renderer.render(painter, self.rect().toRectF())
        painter.end()

    def start(self) -> None:
        self._anim.start()

    def stop(self) -> None:
        self._anim.stop()


class TInputNumber(FocusGlowMixin, BaseWidget):
    """Numeric input with step control, range limits, precision, and rich features.

    Displays a QLineEdit flanked by minus and plus buttons.
    Supports keyboard Up/Down arrow keys, long-press continuous
    increment/decrement, loading state, clearable, status validation,
    custom formatting/parsing, button placement variants, and more.

    Args:
        value: Initial numeric value.
        min: Minimum allowed value (None for unbounded).
        max: Maximum allowed value (None for unbounded).
        step: Increment/decrement step size.
        precision: Decimal precision (0 = integer mode).
        size: Size variant (tiny / small / medium / large).
        disabled: Whether the component is disabled.
        autofocus: Whether to auto-focus on creation.
        loading: Whether to show a loading spinner.
        placeholder: Placeholder text for the input.
        bordered: Whether to show a border.
        show_button: Whether to show +/- buttons.
        button_placement: Button layout ("right" or "both").
        readonly: Whether the input is read-only.
        clearable: Whether to show a clear button.
        round: Whether to render with fully rounded corners.
        status: Validation status (success / warning / error).
        validator: Custom validation function.
        parse: Custom string-to-number parser.
        format_func: Custom number-to-string formatter.
        update_value_on_input: Whether to update value on each keystroke.
        keyboard: Dict controlling keyboard arrow support.
        input_props: Dict of properties to pass to the internal QLineEdit.
        parent: Optional parent widget.

    Signals:
        value_changed: Emitted with the current numeric value after change.
        focused: Emitted when the input gains focus.
        blurred: Emitted when the input loses focus.
        cleared: Emitted when the value is cleared.

    Example:
        >>> num = TInputNumber(value=5, min=0, max=100, step=1)
        >>> num.value_changed.connect(lambda v: print(v))
        >>> num.set_value(42)
    """

    class InputNumberSize(str, Enum):
        """Size variants for TInputNumber."""

        TINY = "tiny"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class InputNumberStatus(str, Enum):
        """Validation status variants for TInputNumber."""

        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    value_changed = Signal(object)
    focused = Signal()
    blurred = Signal()
    cleared = Signal()

    _LONG_PRESS_DELAY_MS = 500
    _REPEAT_INTERVAL_MS = 100

    def __init__(
        self,
        value: int | float = 0,
        min: int | float | None = None,  # noqa: A002
        max: int | float | None = None,  # noqa: A002
        step: int | float = 1,
        precision: int = 0,
        size: InputNumberSize = InputNumberSize.MEDIUM,
        disabled: bool = False,
        autofocus: bool = False,
        loading: bool = False,
        placeholder: str = "",
        bordered: bool = True,
        show_button: bool = True,
        button_placement: str = "right",
        readonly: bool = False,
        clearable: bool = False,
        round: bool = False,  # noqa: A002
        status: InputNumberStatus | None = None,
        validator: Callable[[int | float], bool] | None = None,
        parse: Callable[[str], int | float | None] | None = None,
        format_func: Callable[[int | float], str] | None = None,
        update_value_on_input: bool = True,
        keyboard: dict[str, bool] | None = None,
        input_props: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._init_focus_glow()

        self._min: float | None = float(min) if min is not None else None
        self._max: float | None = float(max) if max is not None else None
        self._step: float = float(step)
        self._precision: int = builtins.max(precision, 0)
        self._size = size
        self._disabled = disabled
        self._value: float = _round_to_precision(
            _clamp(float(value), self._min, self._max), self._precision
        )

        self._autofocus = autofocus
        self._loading = loading
        self._placeholder = placeholder
        self._bordered = bordered
        self._show_button = show_button
        self._button_placement = button_placement
        self._readonly = readonly
        self._clearable = clearable
        self._round = round
        self._status = status
        self._validator_fn = validator
        self._parse_fn = parse
        self._format_fn = format_func
        self._update_value_on_input = update_value_on_input
        self._keyboard = keyboard or {"ArrowUp": True, "ArrowDown": True}
        self._input_props = input_props or {}

        self._hovered = False
        self._focused = False
        self._prefix_widget: QWidget | None = None
        self._suffix_widget: QWidget | None = None

        # Build UI
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(6, 1, 6, 1)
        self._layout.setSpacing(2)

        self._btn_minus = QToolButton(self)
        self._btn_minus.setObjectName("btn_minus")
        self._btn_minus.setText("\u2212")
        self._btn_minus.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._btn_minus.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._line_edit = QLineEdit(self)
        self._line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._line_edit.setTextMargins(0, 0, 0, 0)
        if placeholder:
            self._line_edit.setPlaceholderText(placeholder)

        self._btn_plus = QToolButton(self)
        self._btn_plus.setObjectName("btn_plus")
        self._btn_plus.setText("+")
        self._btn_plus.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._btn_plus.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._btn_clear = QToolButton(self)
        self._btn_clear.setObjectName("btn_clear")
        self._btn_clear.setIcon(_text_icon("\u2715", color=self._current_icon_color()))
        self._btn_clear.setToolTip("Clear")
        self._btn_clear.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._btn_clear.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._btn_clear.setVisible(False)
        self._btn_clear.clicked.connect(self._on_clear_clicked)

        self._apply_button_layout()

        for prop_key, prop_val in self._input_props.items():
            self._line_edit.setProperty(prop_key, prop_val)

        self._apply_validator()
        self._sync_display()

        self.setProperty("inputNumberSize", size.value)
        self.setProperty("disabled", str(disabled).lower())
        self.setProperty("hovered", "false")
        self.setProperty("focused", "false")
        self.setProperty("bordered", str(bordered).lower())
        self.setProperty("round", str(round).lower())
        self.setProperty("buttonPlacement", button_placement)
        self.setProperty("showButton", str(show_button).lower())
        if status is not None:
            self.setProperty("status", status.value)

        self._spinner: _SpinnerWidget | None = None
        if loading:
            self._setup_spinner()

        self._repeat_timer = QTimer(self)
        self._repeat_timer.setInterval(self._REPEAT_INTERVAL_MS)
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.setInterval(self._LONG_PRESS_DELAY_MS)
        self._repeat_direction: int = 0

        self._btn_minus.pressed.connect(self._on_minus_pressed)
        self._btn_minus.released.connect(self._on_button_released)
        self._btn_plus.pressed.connect(self._on_plus_pressed)
        self._btn_plus.released.connect(self._on_button_released)
        self._long_press_timer.timeout.connect(self._on_long_press_start)
        self._repeat_timer.timeout.connect(self._on_repeat_tick)
        self._line_edit.editingFinished.connect(self._on_editing_finished)
        if update_value_on_input:
            self._line_edit.textChanged.connect(self._on_text_input_changed)

        self._line_edit.installEventFilter(self)

        if disabled:
            self._apply_disabled_state(True)
        if readonly:
            self._apply_readonly_state(True)

        self.apply_theme()

        if autofocus:
            QTimer.singleShot(0, self._line_edit.setFocus)

    # -- Public API --

    def get_value(self) -> int | float:
        """Return the current numeric value.

        Returns:
            Current value, as int when precision is 0, else float.
        """
        if self._precision == 0:
            return int(self._value)
        return self._value

    def set_value(self, value: int | float) -> None:
        """Set the numeric value, clamping to [min, max] and rounding to precision.

        Args:
            value: New numeric value.
        """
        clamped = _round_to_precision(_clamp(float(value), self._min, self._max), self._precision)
        old = self._value
        self._value = clamped
        self._sync_display()
        self._update_clear_visibility()
        if clamped != old:
            self.value_changed.emit(self.get_value())

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable the component.

        Args:
            disabled: True to disable all interaction.
        """
        self._disabled = disabled
        self.setProperty("disabled", str(disabled).lower())
        self._apply_disabled_state(disabled)
        self._repolish()

    @property
    def size(self) -> InputNumberSize:
        """Return the current size variant."""
        return self._size

    def set_size(self, size: InputNumberSize) -> None:
        """Set the size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("inputNumberSize", size.value)
        self.apply_theme()
        self.updateGeometry()
        self._position_spinner()

    @property
    def step_val(self) -> float:
        """Return the current step value."""
        return self._step

    @property
    def precision_val(self) -> int:
        """Return the current decimal precision."""
        return self._precision

    @property
    def min_val(self) -> float | None:
        """Return the minimum allowed value, or None if unbounded."""
        return self._min

    @property
    def max_val(self) -> float | None:
        """Return the maximum allowed value, or None if unbounded."""
        return self._max

    @property
    def is_disabled(self) -> bool:
        """Return whether the component is disabled."""
        return self._disabled

    @property
    def is_loading(self) -> bool:
        """Return whether the component is in loading state."""
        return self._loading

    @property
    def is_readonly(self) -> bool:
        """Return whether the component is read-only."""
        return self._readonly

    @property
    def is_clearable(self) -> bool:
        """Return whether the component is clearable."""
        return self._clearable

    @property
    def is_bordered(self) -> bool:
        """Return whether the component shows a border."""
        return self._bordered

    @property
    def is_round(self) -> bool:
        """Return whether the component has rounded corners."""
        return self._round

    @property
    def status(self) -> InputNumberStatus | None:
        """Return the current validation status."""
        return self._status

    @property
    def button_placement(self) -> str:
        """Return the current button placement mode."""
        return self._button_placement

    @property
    def show_button(self) -> bool:
        """Return whether +/- buttons are shown."""
        return self._show_button

    def set_loading(self, loading: bool) -> None:
        """Set the loading state.

        Args:
            loading: True to show spinner and block step operations.
        """
        self._loading = loading
        if loading:
            self._setup_spinner()
            # Hide clear button to prevent overlap with spinner
            self._btn_clear.setVisible(False)
        else:
            if self._spinner is not None:
                self._spinner.stop()
                self._spinner.setVisible(False)
            # Restore clear button if clearable and has text
            if self._clearable:
                has_text = bool(self._line_edit.text().strip())
                self._btn_clear.setVisible(has_text)
        self._btn_minus.setEnabled(not loading and not self._disabled and not self._readonly)
        self._btn_plus.setEnabled(not loading and not self._disabled and not self._readonly)

    def set_readonly(self, readonly: bool) -> None:
        """Set the read-only state.

        Args:
            readonly: True to prevent editing and stepping.
        """
        self._readonly = readonly
        self._apply_readonly_state(readonly)

    def set_clearable(self, clearable: bool) -> None:
        """Set whether the input is clearable.

        Args:
            clearable: True to show clear button when value is present.
        """
        self._clearable = clearable
        self._update_clear_visibility()

    def set_status(self, status: InputNumberStatus | None) -> None:
        """Set the validation status.

        Args:
            status: Validation status or None to clear.
        """
        self._status = status
        if status is not None:
            self.setProperty("status", status.value)
        else:
            self.setProperty("status", "")
        self._repolish()
        self.update()

    def set_bordered(self, bordered: bool) -> None:
        """Set whether to show a border.

        Args:
            bordered: True to show border.
        """
        self._bordered = bordered
        self.setProperty("bordered", str(bordered).lower())
        self._repolish()
        self.update()

    def set_round(self, round_: bool) -> None:
        """Set whether to use rounded corners.

        Args:
            round_: True for fully rounded corners.
        """
        self._round = round_
        self.setProperty("round", str(round_).lower())
        self._repolish()
        self.update()

    def set_show_button(self, show: bool) -> None:
        """Set whether to show +/- buttons.

        Args:
            show: True to show buttons.
        """
        self._show_button = show
        self.setProperty("showButton", str(show).lower())
        self._apply_button_layout()
        self._repolish()

    def set_button_placement(self, placement: str) -> None:
        """Set the button placement mode.

        Args:
            placement: "right" or "both".
        """
        self._button_placement = placement
        self.setProperty("buttonPlacement", placement)
        self._apply_button_layout()
        self._repolish()

    def set_prefix(self, widget: QWidget) -> None:
        """Set a custom prefix widget before the input.

        Args:
            widget: Widget to display as prefix.
        """
        if self._prefix_widget is not None:
            self._layout.removeWidget(self._prefix_widget)
            self._prefix_widget.setParent(None)  # type: ignore[call-overload]
        self._prefix_widget = widget
        self._apply_button_layout()

    def set_suffix(self, widget: QWidget) -> None:
        """Set a custom suffix widget after the input.

        Args:
            widget: Widget to display as suffix.
        """
        if self._suffix_widget is not None:
            self._layout.removeWidget(self._suffix_widget)
            self._suffix_widget.setParent(None)  # type: ignore[call-overload]
        self._suffix_widget = widget
        self._apply_button_layout()

    def set_add_icon(self, icon: QIcon) -> None:
        """Set a custom icon for the plus button.

        Args:
            icon: QIcon for the add button.
        """
        self._btn_plus.setIcon(icon)
        self._btn_plus.setText("")

    def set_minus_icon(self, icon: QIcon) -> None:
        """Set a custom icon for the minus button.

        Args:
            icon: QIcon for the minus button.
        """
        self._btn_minus.setIcon(icon)
        self._btn_minus.setText("")

    # -- Theme --

    def _current_icon_color(self) -> QColor:
        """Return the current theme's icon color as QColor."""
        try:
            engine = ThemeEngine.instance()
            color_str = engine.get_token("colors", "text_primary")
            return parse_color(str(color_str))
        except Exception:
            return QColor("#333639")

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this input number component."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("inputnumber.qss.j2")
            self.setStyleSheet(qss)
            self._repolish()
        except Exception:
            pass
        if hasattr(self, "_btn_clear"):
            self._btn_clear.setIcon(_text_icon("\u2715", color=self._current_icon_color()))

    # -- Private helpers --

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _sync_display(self) -> None:
        """Update the QLineEdit text to reflect the internal value."""
        if self._format_fn is not None:
            self._line_edit.setText(self._format_fn(self.get_value()))
        elif self._precision == 0:
            self._line_edit.setText(str(int(self._value)))
        else:
            self._line_edit.setText(f"{self._value:.{self._precision}f}")

    def _apply_validator(self) -> None:
        """Set the appropriate QValidator on the line edit."""
        if self._parse_fn is not None:
            self._line_edit.setValidator(None)
            return
        if self._precision == 0:
            validator = QIntValidator(self)
            if self._min is not None:
                validator.setBottom(int(self._min))
            if self._max is not None:
                validator.setTop(int(self._max))
            self._line_edit.setValidator(validator)
        else:
            dv = QDoubleValidator(self)
            dv.setDecimals(self._precision)
            if self._min is not None:
                dv.setBottom(self._min)
            if self._max is not None:
                dv.setTop(self._max)
            dv.setNotation(QDoubleValidator.Notation.StandardNotation)
            self._line_edit.setValidator(dv)

    def _apply_disabled_state(self, disabled: bool) -> None:
        """Apply or remove the disabled state on child widgets."""
        self._line_edit.setEnabled(not disabled)
        self._btn_minus.setEnabled(not disabled)
        self._btn_plus.setEnabled(not disabled)
        self.setEnabled(not disabled)

    def _apply_readonly_state(self, readonly: bool) -> None:
        """Apply or remove the read-only state."""
        self._line_edit.setReadOnly(readonly)
        self._btn_minus.setEnabled(not readonly and not self._disabled and not self._loading)
        self._btn_plus.setEnabled(not readonly and not self._disabled and not self._loading)

    def _apply_button_layout(self) -> None:
        """Rebuild the layout based on button_placement and show_button."""
        while self._layout.count():
            self._layout.takeAt(0)

        if not self._show_button:
            if self._prefix_widget:
                self._layout.addWidget(self._prefix_widget)
            self._layout.addWidget(self._line_edit)
            self._layout.addWidget(self._btn_clear)
            if self._suffix_widget:
                self._layout.addWidget(self._suffix_widget)
            self._btn_minus.setVisible(False)
            self._btn_plus.setVisible(False)
            return

        self._btn_minus.setVisible(True)
        self._btn_plus.setVisible(True)

        if self._button_placement == "both":
            self._layout.addWidget(self._btn_minus)
            if self._prefix_widget:
                self._layout.addWidget(self._prefix_widget)
            self._layout.addWidget(self._line_edit)
            self._layout.addWidget(self._btn_clear)
            if self._suffix_widget:
                self._layout.addWidget(self._suffix_widget)
            self._layout.addWidget(self._btn_plus)
        else:
            if self._prefix_widget:
                self._layout.addWidget(self._prefix_widget)
            self._layout.addWidget(self._line_edit)
            self._layout.addWidget(self._btn_clear)
            if self._suffix_widget:
                self._layout.addWidget(self._suffix_widget)
            self._layout.addWidget(self._btn_minus)
            self._layout.addWidget(self._btn_plus)

    def _setup_spinner(self) -> None:
        """Create and show the loading spinner."""
        if self._spinner is None:
            try:
                engine = ThemeEngine.instance()
                color = str(engine.get_token("colors", "text_secondary"))
            except Exception:
                color = "#667085"
            self._spinner = _SpinnerWidget(self._line_edit, color=color)
        self._spinner.setVisible(True)
        self._spinner.start()
        self._spinner.raise_()
        self._position_spinner()

    def _position_spinner(self) -> None:
        """Position the spinner at the right side of the line edit, vertically centered."""
        if self._spinner is None or not self._spinner.isVisible():
            return
        le = self._line_edit
        margin = 2
        x = le.width() - self._spinner.width() - margin
        y = (le.height() - self._spinner.height()) // 2
        self._spinner.move(builtins.max(x, 0), builtins.max(y, 0))

    def _update_clear_visibility(self) -> None:
        """Show or hide the clear button based on current text and loading state."""
        has_text = bool(self._line_edit.text().strip())
        self._btn_clear.setVisible(has_text and self._clearable and not self._loading)

    def _step_value(self, direction: int) -> None:
        """Increment or decrement the value by one step."""
        if self._disabled or self._loading or self._readonly:
            return
        new_val = self._value + direction * self._step
        clamped = _round_to_precision(_clamp(new_val, self._min, self._max), self._precision)
        if clamped != self._value:
            self._value = clamped
            self._sync_display()
            self._update_clear_visibility()
            self.value_changed.emit(self.get_value())

    # -- Button press / long-press handlers --

    def _on_minus_pressed(self) -> None:
        self._step_value(-1)
        self._repeat_direction = -1
        self._long_press_timer.start()

    def _on_plus_pressed(self) -> None:
        self._step_value(1)
        self._repeat_direction = 1
        self._long_press_timer.start()

    def _on_button_released(self) -> None:
        self._long_press_timer.stop()
        self._repeat_timer.stop()
        self._repeat_direction = 0

    def _on_long_press_start(self) -> None:
        self._repeat_timer.start()

    def _on_repeat_tick(self) -> None:
        if self._repeat_direction != 0:
            self._step_value(self._repeat_direction)

    def _on_editing_finished(self) -> None:
        """Commit the text in the line edit as the new value."""
        text = self._line_edit.text().strip()
        if not text or text in ("-", "+", "."):
            self._sync_display()
            return
        if self._parse_fn is not None:
            parsed = self._parse_fn(text)
            if parsed is None:
                self._sync_display()
                return
            parsed_val = float(parsed)
        else:
            try:
                parsed_val = float(text)
            except ValueError:
                self._sync_display()
                return
        if self._validator_fn is not None and not self._validator_fn(parsed_val):
            self._sync_display()
            return
        self.set_value(parsed_val)

    def _on_text_input_changed(self, text: str) -> None:
        """Handle real-time text input changes when update_value_on_input is True."""
        text = text.strip()
        if not text or text in ("-", "+", "."):
            return
        if self._parse_fn is not None:
            parsed = self._parse_fn(text)
            if parsed is None:
                return
            val = float(parsed)
        else:
            try:
                val = float(text)
            except ValueError:
                return
        clamped = _round_to_precision(_clamp(val, self._min, self._max), self._precision)
        if clamped != self._value:
            self._value = clamped
            self.value_changed.emit(self.get_value())
        self._update_clear_visibility()

    def _on_clear_clicked(self) -> None:
        """Handle clear action click."""
        self._line_edit.clear()
        self._value = _round_to_precision(
            _clamp(0.0, self._min, self._max), self._precision
        )
        self._sync_display()
        self._update_clear_visibility()
        self.cleared.emit()
        self.value_changed.emit(self.get_value())

    # -- Paint border manually --

    def paintEvent(self, _event: Any) -> None:  # noqa: N802
        """Paint the rounded rectangle border around the component."""
        if not self._bordered:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            engine = ThemeEngine.instance()
            if self._status is not None:
                status_colors = {
                    self.InputNumberStatus.SUCCESS: "success",
                    self.InputNumberStatus.WARNING: "warning",
                    self.InputNumberStatus.ERROR: "error",
                }
                color_key = status_colors.get(self._status, "border")
                color = parse_color(str(engine.get_token("colors", color_key)))
            elif self._focused:
                color = parse_color(str(engine.get_token("colors", "border_focus")))
            elif self._hovered:
                color = parse_color(str(engine.get_token("colors", "primary_hover")))
            else:
                color = parse_color(str(engine.get_token("colors", "border")))
            try:
                bg = parse_color(str(engine.get_token("colors", "input_color")))
            except (RuntimeError, KeyError):
                bg = parse_color(str(engine.get_token("colors", "bg_default")))
            radius = int(engine.get_token("radius", "medium"))
        except Exception:
            color = QColor("#e0e0e6")
            bg = QColor("#ffffff")
            radius = 4

        if self._round:
            radius = self.height() // 2

        pen = QPen(color)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(bg)
        rect = QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()

    # -- Key event filter for Up/Down arrows + focus tracking --

    def enterEvent(self, event: Any) -> None:  # noqa: N802
        """Track mouse enter to update outer border color."""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def resizeEvent(self, event: Any) -> None:  # noqa: N802
        """Reposition spinner on resize."""
        super().resizeEvent(event)
        self._position_spinner()

    def leaveEvent(self, event: Any) -> None:  # noqa: N802
        """Track mouse leave to restore outer border color."""
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def eventFilter(self, obj: Any, event: Any) -> bool:  # noqa: N802
        """Intercept key events on the line edit for Up/Down arrow support,
        and track focus changes to update outer border.
        """
        if obj is self._line_edit:
            if isinstance(event, QKeyEvent):
                if event.type() == QKeyEvent.Type.KeyPress:
                    if event.key() == Qt.Key.Key_Up and self._keyboard.get("ArrowUp", True):
                        self._step_value(1)
                        return True
                    if event.key() == Qt.Key.Key_Down and self._keyboard.get("ArrowDown", True):
                        self._step_value(-1)
                        return True
            from PySide6.QtCore import QEvent as _QEvent
            if event.type() == _QEvent.Type.FocusIn:
                self._focused = True
                self.update()
                self.focused.emit()
            elif event.type() == _QEvent.Type.FocusOut:
                self._focused = False
                self.update()
                self.blurred.emit()
            elif event.type() == _QEvent.Type.Resize:
                self._position_spinner()
        return super().eventFilter(obj, event)

    def cleanup(self) -> None:
        """Stop timers and disconnect signals before destruction."""
        self._repeat_timer.stop()
        self._long_press_timer.stop()
        if self._spinner is not None:
            self._spinner.stop()
        super().cleanup()
