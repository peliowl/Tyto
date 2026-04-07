"""TInput atom component: a feature-rich text input field.

Supports prefix/suffix icons, clearable mode, and password mode with
visibility toggle. Emits text_changed and cleared signals.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


class TInput(
    FocusGlowMixin,
    BaseWidget,
):
    """Text input component with prefix/suffix icons, clear, and password mode.

    Emits ``text_changed`` when the text content changes and ``cleared``
    when the clear button is clicked.

    Args:
        placeholder: Placeholder text shown when the input is empty.
        clearable: Whether to show a clear button when text is present.
        password: Whether to mask the input text (password mode).
        prefix_icon: Optional icon displayed before the text.
        suffix_icon: Optional icon displayed after the text.
        parent: Optional parent widget.

    Signals:
        text_changed: Emitted with the current text value on every change.
        cleared: Emitted when the clear button is clicked.

    Example:
        >>> inp = TInput(placeholder="Enter name", clearable=True)
        >>> inp.text_changed.connect(lambda t: print(f"Text: {t}"))
    """

    text_changed = Signal(str)
    cleared = Signal()

    def __init__(
        self,
        placeholder: str = "",
        clearable: bool = False,
        password: bool = False,
        prefix_icon: QIcon | None = None,
        suffix_icon: QIcon | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._init_focus_glow()

        self._clearable = clearable
        self._password = password
        self._password_visible = False

        # Layout: [prefix_icon] [line_edit] [clear_btn] [toggle_btn] [suffix_icon]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Prefix icon button
        self._prefix_btn: QToolButton | None = None
        if prefix_icon is not None:
            self._prefix_btn = QToolButton(self)
            self._prefix_btn.setIcon(prefix_icon)
            self._prefix_btn.setFixedSize(QSize(24, 24))
            self._prefix_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._layout.addWidget(self._prefix_btn)

        # Core line edit
        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText(placeholder)
        if password:
            self._line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._layout.addWidget(self._line_edit)

        # Clear button (hidden by default)
        self._clear_btn: QToolButton | None = None
        if clearable:
            self._clear_btn = QToolButton(self)
            self._clear_btn.setText("\u2715")  # Unicode X mark
            self._clear_btn.setFixedSize(QSize(24, 24))
            self._clear_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._clear_btn.setVisible(False)
            self._clear_btn.clicked.connect(self._on_clear_clicked)
            self._layout.addWidget(self._clear_btn)

        # Password visibility toggle button
        self._toggle_btn: QToolButton | None = None
        if password:
            self._toggle_btn = QToolButton(self)
            self._toggle_btn.setText("\u25cf")  # Filled circle (eye-closed hint)
            self._toggle_btn.setFixedSize(QSize(24, 24))
            self._toggle_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._toggle_btn.clicked.connect(self.toggle_password_visibility)
            self._layout.addWidget(self._toggle_btn)

        # Suffix icon button
        self._suffix_btn: QToolButton | None = None
        if suffix_icon is not None:
            self._suffix_btn = QToolButton(self)
            self._suffix_btn.setIcon(suffix_icon)
            self._suffix_btn.setFixedSize(QSize(24, 24))
            self._suffix_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._layout.addWidget(self._suffix_btn)

        self.setFocusProxy(self._line_edit)
        self.apply_theme()

    # -- Public API --

    def get_text(self) -> str:
        """Return the current text content.

        Returns:
            The text string in the input field.
        """
        return self._line_edit.text()

    def set_text(self, text: str) -> None:
        """Set the text content programmatically.

        Args:
            text: The new text to display.
        """
        self._line_edit.setText(text)

    def clear(self) -> None:
        """Clear the input text and emit the cleared signal."""
        self._line_edit.clear()
        self.cleared.emit()

    def toggle_password_visibility(self) -> None:
        """Toggle between masked and plain-text display in password mode."""
        if not self._password:
            return
        self._password_visible = not self._password_visible
        if self._password_visible:
            self._line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            if self._toggle_btn is not None:
                self._toggle_btn.setText("\u25cb")  # Open circle (eye-open hint)
        else:
            self._line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            if self._toggle_btn is not None:
                self._toggle_btn.setText("\u25cf")  # Filled circle (eye-closed hint)

    # -- Theme --

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

    # -- Size hint --

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(200, 34)

    # -- Private --

    def _on_text_changed(self, text: str) -> None:
        """Handle internal QLineEdit text changes.

        Args:
            text: The new text value.
        """
        if self._clear_btn is not None:
            self._clear_btn.setVisible(bool(text))
        self.text_changed.emit(text)

    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        self._line_edit.clear()
        self.cleared.emit()
