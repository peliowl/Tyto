"""TopBar view: title label and theme toggle switch for the Playground."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from examples.playground.styles.playground_styles import PlaygroundStyles
from examples.playground.viewmodels.playground_viewmodel import PlaygroundViewModel
from tyto_ui_lib import TSwitch, ThemeEngine


class TopBar(QWidget):
    """Top bar containing the playground title and a dark-mode toggle.

    The TSwitch is wired to ``PlaygroundViewModel.toggle_theme`` so that
    flipping the switch changes the active theme globally.

    Args:
        viewmodel: The playground view-model that owns theme state.
        parent: Optional parent widget.
    """

    def __init__(self, viewmodel: PlaygroundViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("top_bar")
        self._viewmodel = viewmodel

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)

        # Title
        title = QLabel("Tyto UI Playground")
        title.setObjectName("top_bar_title")
        layout.addWidget(title)

        layout.addStretch()

        # Theme label + switch
        theme_label = QLabel("Dark Mode")
        theme_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(theme_label)

        self._theme_switch = TSwitch(checked=False)
        self._theme_switch.toggled.connect(viewmodel.toggle_theme)
        layout.addWidget(self._theme_switch)

        # Apply initial style and listen for theme changes
        self._apply_style()
        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Slot: refresh QSS when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware QSS from PlaygroundStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(PlaygroundStyles.top_bar_style(theme))
