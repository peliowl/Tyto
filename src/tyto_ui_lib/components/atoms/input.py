"""TInput atom component: a feature-rich text input field.

Supports prefix/suffix icons, clearable mode, password mode with
visibility toggle, textarea mode, size variants, status validation,
loading animation, show_count, maxlength, autosize, and more.
Emits text_changed and cleared signals.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QInputMethodEvent,
    QPainter,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


def _text_icon(char: str, size: int = 16, color: QColor | None = None) -> QIcon:
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


# Simple circular-arc SVG used as the loading spinner icon.
_SPINNER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
    '<circle cx="8" cy="8" r="6" fill="none" stroke="currentColor"'
    ' stroke-width="2" stroke-dasharray="28 10" stroke-linecap="round"/>'
    "</svg>"
)

# Eye icon SVGs for password visibility toggle (NaiveUI style).
_EYE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
    '<path d="M256 128C140.6 128 44.7 192 0 256c44.7 64 140.6 128 256 128'
    's211.3-64 256-128c-44.7-64-140.6-128-256-128zm0 208'
    'a80 80 0 1 1 0-160 80 80 0 0 1 0 160z" fill="{color}"/>'
    '</svg>'
)

_EYE_OFF_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
    '<path d="M432.5 388.2L73.5 73.5 51.3 95.7l89.5 89.5C74.5 220.5 28.5 256 0 256'
    'c44.7 64 140.6 128 256 128 39.8 0 77.3-9.4 110.8-25.5l65.7 65.7 22.2-22.2z'
    'M256 336a80 80 0 0 1-68.4-121.6l96 96A79.6 79.6 0 0 1 256 336z'
    'M512 256c-44.7-64-140.6-128-256-128-27.2 0-53.3 4.4-77.8 12.3'
    'l50.5 50.5A80 80 0 0 1 336 298.3l72.2 72.2C454.5 335.2 489.5 295.5 512 256z" fill="{color}"/>'
    '</svg>'
)


def _parse_color(color_str: str) -> QColor:
    """Parse a CSS color string into a QColor.

    Handles formats that QColor doesn't natively support:
    - ``rgba(r, g, b, a)`` where a is 0.0-1.0
    - ``rgb(r, g, b)``
    - Standard hex ``#RRGGBB`` / ``#AARRGGBB``
    """
    s = color_str.strip()
    if s.startswith("rgba(") and s.endswith(")"):
        parts = s[5:-1].split(",")
        if len(parts) == 4:
            r, g, b = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
            a = float(parts[3].strip())
            c = QColor(r, g, b)
            c.setAlphaF(a)
            return c
    if s.startswith("rgb(") and s.endswith(")"):
        parts = s[4:-1].split(",")
        if len(parts) == 3:
            r, g, b = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
            return QColor(r, g, b)
    c = QColor(s)
    return c if c.isValid() else QColor("#667085")


def _to_svg_color(color: str) -> str:
    """Convert any CSS color string to an SVG-compatible color.

    SVG fill/stroke attributes don't support CSS rgba() syntax.
    Converts through _parse_color/QColor to produce rgb(r,g,b) format.
    """
    c = _parse_color(color)
    return f"rgb({c.red()},{c.green()},{c.blue()})"


def _svg_icon(svg_template: str, size: int = 16, color: str = "#667085") -> QIcon:
    """Create a QIcon from an SVG template string with color substitution."""
    svg_color = _to_svg_color(color)
    svg_data = svg_template.format(color=svg_color).encode()
    renderer = QSvgRenderer(svg_data)
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    renderer.render(painter)
    painter.end()
    return QIcon(px)


class _InputSpinnerWidget(QWidget):
    """Internal widget that renders a rotating SVG spinner for loading state."""

    def __init__(self, parent: QWidget | None = None, color: str = "#667085") -> None:
        super().__init__(parent)
        self._color = color
        self._renderer = QSvgRenderer(self._build_svg(color), self)
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
        """Build spinner SVG with the given stroke color."""
        svg_color = _to_svg_color(color)
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
            f'<circle cx="8" cy="8" r="6" fill="none" stroke="{svg_color}"'
            ' stroke-width="2" stroke-dasharray="28 10" stroke-linecap="round"/>'
            '</svg>'
        ).encode()

    def set_color(self, color: str) -> None:
        """Update the spinner stroke color."""
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


class _IMEAwarePlainTextEdit(QPlainTextEdit):
    """QPlainTextEdit subclass that hides placeholder text during IME composition.

    The default QPlainTextEdit keeps showing placeholder text while the user
    is composing characters via an Input Method Editor (e.g. Chinese pinyin).
    This subclass detects active composition via ``inputMethodEvent`` and
    temporarily clears the placeholder so it does not overlap the preedit text.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._saved_placeholder: str = ""
        self._composing: bool = False

    def inputMethodEvent(self, event: QInputMethodEvent) -> None:  # noqa: N802
        """Hide placeholder when IME composition starts, restore when it ends."""
        preedit = event.preeditString()
        if preedit and not self._composing:
            # Composition started — hide placeholder
            self._composing = True
            self._saved_placeholder = self.placeholderText()
            self.setPlaceholderText("")
        elif not preedit and self._composing:
            # Composition ended — restore placeholder
            self._composing = False
            self.setPlaceholderText(self._saved_placeholder)
        super().inputMethodEvent(event)


class TInput(
    FocusGlowMixin,
    BaseWidget,
):
    """Text input component with prefix/suffix icons, clear, password, textarea,
    size variants, status validation, loading, show_count, and more.

    Emits ``text_changed`` when the text content changes and ``cleared``
    when the clear button is clicked.

    Args:
        placeholder: Placeholder text shown when the input is empty.
        clearable: Whether to show a clear button when text is present.
        password: Whether to mask the input text (password mode). Shorthand
            for input_type=PASSWORD.
        input_type: Input mode (TEXT, TEXTAREA, PASSWORD).
        size: Size variant (tiny/small/medium/large).
        round: Whether to render with fully rounded corners.
        bordered: Whether to show a border.
        maxlength: Maximum allowed text length.
        minlength: Minimum required text length (marks invalid if shorter).
        show_count: Whether to display character count.
        readonly: Whether the input is read-only.
        autosize: Auto-resize textarea height. True for default, or dict
            with min_rows/max_rows keys.
        rows: Default number of rows for textarea mode.
        loading: Whether to show a loading spinner.
        status: Validation status (success/warning/error).
        resizable: Whether textarea supports user drag-resize.
        show_password_on: Password visibility trigger ("click" or "mousedown").
        prefix_icon: Optional icon displayed before the text.
        suffix_icon: Optional icon displayed after the text.
        parent: Optional parent widget.

    Signals:
        text_changed: Emitted with the current text value on every change.
        cleared: Emitted when the clear button is clicked.

    Example:
        >>> inp = TInput(placeholder="Enter name", clearable=True, size=TInput.InputSize.LARGE)
        >>> inp.text_changed.connect(lambda t: print(f"Text: {t}"))
    """

    class InputType(str, Enum):
        """Input mode variants for TInput."""

        TEXT = "text"
        TEXTAREA = "textarea"
        PASSWORD = "password"

    class InputSize(str, Enum):
        """Size variants for TInput."""

        TINY = "tiny"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class InputStatus(str, Enum):
        """Validation status variants for TInput."""

        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    text_changed = Signal(str)
    cleared = Signal()

    def __init__(
        self,
        placeholder: str = "",
        clearable: bool = False,
        password: bool = False,
        input_type: InputType | None = None,
        size: InputSize = InputSize.MEDIUM,
        round: bool = False,
        bordered: bool = True,
        maxlength: int | None = None,
        minlength: int | None = None,
        show_count: bool = False,
        readonly: bool = False,
        autosize: dict[str, int] | bool = False,
        rows: int = 3,
        loading: bool = False,
        status: InputStatus | None = None,
        resizable: bool = False,
        show_password_on: str = "click",
        prefix_icon: QIcon | None = None,
        suffix_icon: QIcon | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._init_focus_glow()

        # Resolve input_type from password shorthand
        if input_type is not None:
            self._input_type = input_type
        elif password:
            self._input_type = self.InputType.PASSWORD
        else:
            self._input_type = self.InputType.TEXT

        self._size = size
        self._round = round
        self._bordered = bordered
        self._maxlength = maxlength
        self._minlength = minlength
        self._show_count = show_count
        self._readonly = readonly
        self._autosize = autosize
        self._rows = rows
        self._loading = loading
        self._status = status
        self._resizable = resizable
        self._show_password_on = show_password_on
        self._clearable = clearable
        self._password = self._input_type == self.InputType.PASSWORD
        self._password_visible = False
        self._is_textarea = self._input_type == self.InputType.TEXTAREA

        # Main vertical layout: [input_row] [count_label]
        self._outer_layout = QVBoxLayout(self)
        self._outer_layout.setContentsMargins(0, 0, 0, 0)
        self._outer_layout.setSpacing(2)

        # Input row layout: [prefix_icon] [editor] [spinner] [suffix_icon]
        self._row_widget = QWidget(self)
        self._layout = QHBoxLayout(self._row_widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._outer_layout.addWidget(self._row_widget)

        # Prefix icon button
        self._prefix_btn: QToolButton | None = None
        if prefix_icon is not None:
            self._prefix_btn = QToolButton(self)
            self._prefix_btn.setIcon(prefix_icon)
            self._prefix_btn.setFixedSize(QSize(24, 24))
            self._prefix_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._layout.addWidget(self._prefix_btn)

        # Build the appropriate editor widget
        self._line_edit: QLineEdit | None = None
        self._text_edit: QPlainTextEdit | None = None
        self._clear_action: QAction | None = None
        self._toggle_action: QAction | None = None

        if self._is_textarea:
            self._build_textarea(placeholder)
        else:
            self._build_line_edit(placeholder)

        # Loading spinner — uses a trailing QAction inside QLineEdit
        # (for textarea mode, falls back to a widget in the outer layout)
        self._spinner = _InputSpinnerWidget(self, color=self._current_icon_color_str())
        self._spinner.setVisible(False)
        self._loading_action: QAction | None = None
        if not self._is_textarea and self._line_edit is not None:
            # Place spinner as a trailing action inside QLineEdit
            self._loading_action = QAction(self._line_edit)
            self._loading_action.setIcon(QIcon())
            self._line_edit.addAction(self._loading_action, QLineEdit.ActionPosition.TrailingPosition)
            self._loading_action.setVisible(False)
            # Position the spinner widget over the action area
            self._spinner.setParent(self._line_edit)
            self._spinner.raise_()
        else:
            self._layout.addWidget(self._spinner)

        # Suffix icon button
        self._suffix_btn: QToolButton | None = None
        if suffix_icon is not None:
            self._suffix_btn = QToolButton(self)
            self._suffix_btn.setIcon(suffix_icon)
            self._suffix_btn.setFixedSize(QSize(24, 24))
            self._suffix_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._layout.addWidget(self._suffix_btn)

        # Character count label
        self._count_label: QLabel | None = None
        if show_count:
            self._count_label = QLabel(self)
            self._count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self._count_label.setObjectName("inputCountLabel")
            self._outer_layout.addWidget(self._count_label)
            self._update_count_display()

        # Set focus proxy
        if self._line_edit is not None:
            self.setFocusProxy(self._line_edit)
        elif self._text_edit is not None:
            self.setFocusProxy(self._text_edit)

        # Apply QSS dynamic properties
        self.setProperty("inputType", self._input_type.value)
        self.setProperty("inputSize", size.value)
        self.setProperty("round", str(round).lower())
        self.setProperty("bordered", str(bordered).lower())
        if status is not None:
            self.setProperty("status", status.value)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Apply loading state
        if loading:
            self.set_loading(True)

        # Apply readonly
        if readonly:
            self.set_readonly(True)

        self.apply_theme()

    # -- Private build helpers --

    def _build_line_edit(self, placeholder: str) -> None:
        """Build the QLineEdit-based editor for text/password modes."""
        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText(placeholder)
        if self._password:
            self._line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        if self._maxlength is not None:
            self._line_edit.setMaxLength(self._maxlength)
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._layout.addWidget(self._line_edit)

        # Clear action inside QLineEdit
        if self._clearable:
            self._clear_action = QAction(self._line_edit)
            self._clear_action.setIcon(_text_icon("\u2715", color=self._current_icon_color()))
            self._clear_action.setToolTip("Clear")
            self._line_edit.addAction(self._clear_action, QLineEdit.ActionPosition.TrailingPosition)
            self._clear_action.setVisible(False)
            self._clear_action.triggered.connect(self._on_clear_clicked)

        # Password visibility toggle action inside QLineEdit
        if self._password:
            self._toggle_action = QAction(self._line_edit)
            self._toggle_action.setIcon(_svg_icon(_EYE_OFF_SVG, color=self._current_icon_color_str()))
            self._toggle_action.setToolTip("Toggle password visibility")
            self._line_edit.addAction(self._toggle_action, QLineEdit.ActionPosition.TrailingPosition)
            self._toggle_action.triggered.connect(self.toggle_password_visibility)

    def _build_textarea(self, placeholder: str) -> None:
        """Build the QPlainTextEdit-based editor for textarea mode."""
        self._text_edit = _IMEAwarePlainTextEdit(self)
        self._text_edit.setPlaceholderText(placeholder)
        self._text_edit.textChanged.connect(self._on_textarea_changed)
        self._text_edit.setObjectName("inputTextarea")

        # Apply rows
        fm = self._text_edit.fontMetrics()
        line_h = fm.lineSpacing()
        doc_margin = self._text_edit.document().documentMargin() if self._text_edit.document() else 4
        base_height = int(self._rows * line_h + 2 * doc_margin + 2)
        self._text_edit.setMinimumHeight(base_height)

        # Resizable
        if self._resizable:
            self._text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            self._text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self._text_edit.setFixedHeight(base_height)

        # Autosize overrides fixed height
        if self._autosize:
            self._text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self._text_edit.setMinimumHeight(0)
            self._text_edit.setMaximumHeight(16777215)
            self._text_edit.textChanged.connect(self._adjust_textarea_height)

        self._layout.addWidget(self._text_edit)

    # -- Public properties --

    @property
    def input_type(self) -> InputType:
        """Return the current input type."""
        return self._input_type

    @property
    def size(self) -> InputSize:
        """Return the current input size."""
        return self._size

    @property
    def is_round(self) -> bool:
        """Return whether the input has fully rounded corners."""
        return self._round

    @property
    def bordered(self) -> bool:
        """Return whether the input shows a border."""
        return self._bordered

    @property
    def status(self) -> InputStatus | None:
        """Return the current validation status."""
        return self._status

    @property
    def loading(self) -> bool:
        """Return whether the input is in loading state."""
        return self._loading

    @property
    def readonly(self) -> bool:
        """Return whether the input is read-only."""
        return self._readonly

    @property
    def maxlength(self) -> int | None:
        """Return the maximum text length constraint."""
        return self._maxlength

    @property
    def minlength(self) -> int | None:
        """Return the minimum text length constraint."""
        return self._minlength

    @property
    def show_count(self) -> bool:
        """Return whether character count is displayed."""
        return self._show_count

    # -- Public methods --

    def get_text(self) -> str:
        """Return the current text content.

        Returns:
            The text string in the input field.
        """
        if self._is_textarea and self._text_edit is not None:
            return self._text_edit.toPlainText()
        if self._line_edit is not None:
            return self._line_edit.text()
        return ""

    def set_text(self, text: str) -> None:
        """Set the text content programmatically.

        Args:
            text: The new text to display.
        """
        if self._is_textarea and self._text_edit is not None:
            self._text_edit.setPlainText(text)
        elif self._line_edit is not None:
            self._line_edit.setText(text)

    def clear(self) -> None:
        """Clear the input text and emit the cleared signal."""
        if self._is_textarea and self._text_edit is not None:
            self._text_edit.clear()
        elif self._line_edit is not None:
            self._line_edit.clear()
        self.cleared.emit()

    def get_text_length(self) -> int:
        """Return the current text length.

        Returns:
            Number of characters in the input.
        """
        return len(self.get_text())

    def toggle_password_visibility(self) -> None:
        """Toggle between masked and plain-text display in password mode."""
        if not self._password or self._line_edit is None:
            return
        self._password_visible = not self._password_visible
        if self._password_visible:
            self._line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            if self._toggle_action is not None:
                self._toggle_action.setIcon(_svg_icon(_EYE_SVG, color=self._current_icon_color_str()))
        else:
            self._line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            if self._toggle_action is not None:
                self._toggle_action.setIcon(_svg_icon(_EYE_OFF_SVG, color=self._current_icon_color_str()))

    def set_size(self, size: InputSize) -> None:
        """Change the input size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("inputSize", size.value)
        self._repolish()

    def set_status(self, status: InputStatus | None) -> None:
        """Set the validation status.

        Args:
            status: Validation status, or None to clear.
        """
        self._status = status
        if status is not None:
            self.setProperty("status", status.value)
        else:
            self.setProperty("status", None)
        self._repolish()

    def set_readonly(self, readonly: bool) -> None:
        """Set the read-only state.

        Args:
            readonly: True to make read-only, False to allow editing.
        """
        self._readonly = readonly
        if self._line_edit is not None:
            self._line_edit.setReadOnly(readonly)
        if self._text_edit is not None:
            self._text_edit.setReadOnly(readonly)

    def set_loading(self, loading: bool) -> None:
        """Enter or exit loading state.

        In loading state a spinner replaces other trailing actions
        (clear, password toggle) inside the QLineEdit (NaiveUI style).

        Args:
            loading: True to enter loading state, False to exit.
        """
        self._loading = loading
        if self._loading_action is not None:
            self._loading_action.setVisible(loading)
        self._spinner.setVisible(loading)
        if loading:
            self._spinner.start()
            # Hide other trailing actions to prevent overlap
            if self._clear_action is not None:
                self._clear_action.setVisible(False)
            if self._toggle_action is not None:
                self._toggle_action.setVisible(False)
            if self._line_edit is not None and self._loading_action is not None:
                self._position_spinner_in_line_edit()
        else:
            self._spinner.stop()
            # Restore clear action if clearable and has text
            if self._clear_action is not None and self._clearable:
                has_text = bool(self._line_edit.text()) if self._line_edit else False
                self._clear_action.setVisible(has_text)
            # Restore password toggle if in password mode
            if self._toggle_action is not None and self._password:
                self._toggle_action.setVisible(True)

    def _position_spinner_in_line_edit(self) -> None:
        """Position the spinner widget inside the QLineEdit's trailing area."""
        if self._line_edit is None:
            return
        le = self._line_edit
        sp = self._spinner
        x = le.width() - sp.width() - 6
        y = (le.height() - sp.height()) // 2
        sp.move(x, y)

    def resizeEvent(self, event: object) -> None:  # noqa: N802
        """Reposition the loading spinner when the widget resizes."""
        super().resizeEvent(event)
        if self._loading and self._loading_action is not None:
            self._position_spinner_in_line_edit()

    def set_round(self, round_: bool) -> None:
        """Enable or disable fully rounded corners.

        Args:
            round_: True for capsule shape, False for normal radius.
        """
        self._round = round_
        self.setProperty("round", str(round_).lower())
        if round_:
            self._apply_round_radius()
        else:
            # Remove inline border-radius so QSS template default takes over
            if self._line_edit is not None:
                self._line_edit.setStyleSheet("")
        self._repolish()

    def set_bordered(self, bordered: bool) -> None:
        """Show or hide the input border.

        Args:
            bordered: True to show border, False to hide.
        """
        self._bordered = bordered
        self.setProperty("bordered", str(bordered).lower())
        self._repolish()

    # -- Theme --

    def _current_icon_color(self) -> QColor:
        """Return the current theme's icon color as QColor."""
        try:
            engine = ThemeEngine.instance()
            color_str = engine.get_token("colors", "text_secondary")
            return _parse_color(str(color_str))
        except Exception:
            return QColor("#667085")

    def _current_icon_color_str(self) -> str:
        """Return the current theme's icon color as a CSS string."""
        try:
            engine = ThemeEngine.instance()
            return str(engine.get_token("colors", "text_secondary"))
        except Exception:
            return "#667085"

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this input."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("input.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

        # Apply round border-radius directly on the child editor because
        # QSS parent property selectors (TInput[round="true"] QLineEdit)
        # do not reliably cascade via per-widget setStyleSheet.
        if hasattr(self, "_round") and self._round:
            self._apply_round_radius()

        # Set placeholder text color from token
        try:
            color_str = engine.get_token("colors", "text_secondary")
            color = _parse_color(str(color_str))
            if hasattr(self, "_line_edit") and self._line_edit is not None:
                palette = self._line_edit.palette()
                palette.setColor(palette.ColorRole.PlaceholderText, color)
                self._line_edit.setPalette(palette)
            # Update action icons to match current theme color
            if hasattr(self, "_clear_action") and self._clear_action is not None:
                self._clear_action.setIcon(_text_icon("\u2715", color=color))
            if hasattr(self, "_toggle_action") and self._toggle_action is not None:
                svg = _EYE_SVG if self._password_visible else _EYE_OFF_SVG
                self._toggle_action.setIcon(_svg_icon(svg, color=color.name() if color else "#667085"))
            # Update spinner color
            if hasattr(self, "_spinner") and self._spinner is not None:
                self._spinner.set_color(color_str)
            # Update count label color
            if hasattr(self, "_count_label") and self._count_label is not None:
                self._count_label.setStyleSheet(f"color: {color_str};")
        except Exception:
            pass

        # Repolish self and child editors so property selectors take effect
        self._repolish()

    # -- Size hint --

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size based on current size variant."""
        height_map = {
            self.InputSize.TINY: 22,
            self.InputSize.SMALL: 28,
            self.InputSize.MEDIUM: 34,
            self.InputSize.LARGE: 40,
        }
        h = height_map.get(self._size, 34)
        if self._is_textarea and self._text_edit is not None:
            fm = self._text_edit.fontMetrics()
            h = max(h, self._rows * fm.lineSpacing() + 10)
        return QSize(200, h)

    # -- Private --

    def _apply_round_radius(self) -> None:
        """Apply full round border-radius directly on the child editor widget.

        QSS parent property selectors like ``TInput[round="true"] QLineEdit``
        do not reliably cascade when using per-widget setStyleSheet, so we
        set the border-radius inline on the QLineEdit itself.
        """
        engine = ThemeEngine.instance()
        size_key = self._size.value if hasattr(self, "_size") else "medium"
        try:
            tokens = engine.current_tokens()
            if tokens is not None and size_key in tokens.component_sizes:
                height = tokens.component_sizes[size_key]["height"]
                radius = int(height) // 2
            else:
                radius = 17  # fallback: medium height 34 / 2
        except Exception:
            radius = 17
        if hasattr(self, "_line_edit") and self._line_edit is not None:
            self._line_edit.setStyleSheet(f"border-radius: {radius}px;")

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors.

        Must also repolish child editor widgets so that parent property
        selectors like ``TInput[round="true"] QLineEdit`` take effect.
        Guards with hasattr because apply_theme() may be called from
        BaseWidget.__init__ before child editors are created.
        """
        self.style().unpolish(self)
        self.style().polish(self)
        if hasattr(self, "_line_edit") and self._line_edit is not None:
            self._line_edit.style().unpolish(self._line_edit)
            self._line_edit.style().polish(self._line_edit)
            self._line_edit.update()
        if hasattr(self, "_text_edit") and self._text_edit is not None:
            self._text_edit.style().unpolish(self._text_edit)
            self._text_edit.style().polish(self._text_edit)
            self._text_edit.update()
        self.update()

    def _on_text_changed(self, text: str) -> None:
        """Handle internal QLineEdit text changes."""
        if self._clear_action is not None:
            self._clear_action.setVisible(bool(text) and self._clearable)
        self.text_changed.emit(text)
        if self._show_count:
            self._update_count_display()

    def _on_textarea_changed(self) -> None:
        """Handle internal QPlainTextEdit text changes."""
        if self._text_edit is None:
            return
        text = self._text_edit.toPlainText()

        # Enforce maxlength for textarea
        if self._maxlength is not None and len(text) > self._maxlength:
            cursor = self._text_edit.textCursor()
            pos = cursor.position()
            self._text_edit.blockSignals(True)
            self._text_edit.setPlainText(text[: self._maxlength])
            cursor = self._text_edit.textCursor()
            cursor.setPosition(min(pos, self._maxlength))
            self._text_edit.setTextCursor(cursor)
            self._text_edit.blockSignals(False)
            text = self._text_edit.toPlainText()

        self.text_changed.emit(text)
        if self._show_count:
            self._update_count_display()

    def _on_clear_clicked(self) -> None:
        """Handle clear action click."""
        if self._line_edit is not None:
            self._line_edit.clear()
        self.cleared.emit()

    def _update_count_display(self) -> None:
        """Update the character count label text."""
        if self._count_label is None:
            return
        current = self.get_text_length()
        if self._maxlength is not None:
            self._count_label.setText(f"{current} / {self._maxlength}")
        else:
            self._count_label.setText(str(current))

    def _adjust_textarea_height(self) -> None:
        """Adjust textarea height based on content when autosize is enabled."""
        if self._text_edit is None or not self._autosize:
            return

        doc = self._text_edit.document()
        if doc is None:
            return

        fm = self._text_edit.fontMetrics()
        line_h = fm.lineSpacing()
        doc_margin = doc.documentMargin()
        line_count = max(1, doc.blockCount())

        # Determine min/max rows
        if isinstance(self._autosize, dict):
            min_rows = self._autosize.get("min_rows", 2)
            max_rows = self._autosize.get("max_rows", 10)
        else:
            min_rows = 2
            max_rows = 10

        clamped = max(min_rows, min(line_count, max_rows))
        target_h = int(clamped * line_h + 2 * doc_margin + 2)
        self._text_edit.setFixedHeight(target_h)
