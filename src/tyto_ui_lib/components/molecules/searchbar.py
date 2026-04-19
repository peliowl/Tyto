"""TSearchBar molecule component: search input with submit button.

Combines TInput and TButton atoms into a compact search bar with
search_changed and search_submitted signals.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QHBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.components.atoms.button import TButton
from tyto_ui_lib.components.atoms.input import TInput
from tyto_ui_lib.core.theme_engine import ThemeEngine


class TSearchBar(BaseWidget):
    """Search bar component composed of TInput + TButton.

    Emits ``search_changed`` on every keystroke and ``search_submitted``
    when the user clicks the search button or presses Enter.

    Args:
        placeholder: Placeholder text for the input field.
        clearable: Whether the input shows a clear button.
        parent: Optional parent widget.

    Signals:
        search_changed: Emitted with the current text on every change.
        search_submitted: Emitted with the current text on submit.

    Example:
        >>> bar = TSearchBar(placeholder="Search...", clearable=True)
        >>> bar.search_submitted.connect(lambda t: print(f"Search: {t}"))
    """

    search_changed = Signal(str)
    search_submitted = Signal(str)

    def __init__(
        self,
        placeholder: str = "搜索...",
        clearable: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._input = TInput(
            placeholder=placeholder,
            clearable=clearable,
            parent=self,
        )
        self._input.text_changed.connect(self._on_text_changed)
        self._input.installEventFilter(self)
        self._layout.addWidget(self._input, 1)

        self._button = TButton(
            text="搜索",
            button_type=TButton.ButtonType.PRIMARY,
            parent=self,
        )
        self._button.clicked.connect(self._on_submit)
        self._layout.addWidget(self._button)

        self.apply_theme()

    # -- Public API --

    def get_text(self) -> str:
        """Return the current search text.

        Returns:
            The text string in the search input.
        """
        return self._input.get_text()

    def clear(self) -> None:
        """Clear the search input text."""
        self._input.clear()

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this search bar."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("searchbar.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    # -- Size hint --

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(300, 34)

    # -- Event filter for Enter key --

    def eventFilter(self, obj: object, event: object) -> bool:
        """Intercept Enter key on the input to trigger search submission.

        Args:
            obj: The watched object.
            event: The event to filter.

        Returns:
            True if the event was consumed, False otherwise.
        """
        if obj is self._input and isinstance(event, QKeyEvent):
            if event.type() == QKeyEvent.Type.KeyPress and event.key() in (
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            ):
                self._on_submit()
                return True
        return super().eventFilter(obj, event)

    # -- Private --

    def _on_text_changed(self, text: str) -> None:
        """Forward input text changes as search_changed signal.

        Args:
            text: The new text value.
        """
        self.search_changed.emit(text)
        self._emit_bus_event("search_changed", text)

    def _on_submit(self) -> None:
        """Emit search_submitted with the current text."""
        text = self._input.get_text()
        self.search_submitted.emit(text)
        self._emit_bus_event("search_submitted", text)
