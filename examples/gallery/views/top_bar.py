"""TopBar view: title label and theme toggle switch."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from examples.gallery.styles.gallery_styles import GalleryStyles
from examples.gallery.viewmodels.gallery_viewmodel import GalleryViewModel
from tyto_ui_lib import TSwitch, ThemeEngine


class TopBar(QWidget):
    """Top bar containing the gallery title and a dark-mode toggle.

    The TSwitch is wired to ``GalleryViewModel.toggle_theme`` so that
    flipping the switch changes the active theme globally.

    Args:
        viewmodel: The gallery view-model that owns theme state.
        parent: Optional parent widget.
    """

    def __init__(self, viewmodel: GalleryViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("top_bar")
        self._viewmodel = viewmodel

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)

        # Title
        title = QLabel("Tyto UI Gallery")
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
        """Apply theme-aware QSS from GalleryStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(GalleryStyles.top_bar_style(theme))
