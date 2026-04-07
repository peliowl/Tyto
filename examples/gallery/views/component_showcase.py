"""ComponentShowcase view: right panel displaying the selected component's showcase."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from examples.gallery.styles.gallery_styles import GalleryStyles
from examples.gallery.viewmodels.gallery_viewmodel import GalleryViewModel
from tyto_ui_lib import ThemeEngine


class ComponentShowcase(QScrollArea):
    """Right panel that displays the selected component's showcase.

    Inherits ``QScrollArea`` to support vertical scrolling when the
    showcase content exceeds the visible area.  The ``show_component``
    method looks up the ``showcase_factory`` from the registry and
    swaps in the new widget.

    Args:
        viewmodel: Gallery view-model providing the registry.
        parent: Optional parent widget.
    """

    def __init__(self, viewmodel: GalleryViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Start with an empty placeholder
        self._set_placeholder()

        # Listen for theme changes
        self._apply_style()
        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._on_theme_changed)

    def show_component(self, key: str) -> None:
        """Load and display the showcase for the given component *key*.

        If the key is not found in the registry the panel shows a
        fallback message instead.

        Args:
            key: Registered component key (e.g. ``"button"``).
        """
        registry = self._viewmodel.get_registry()
        info = registry.get_by_key(key)
        if info is None:
            self._set_placeholder(f"Component '{key}' not found.")
            return

        # Build the showcase widget via the registered factory
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 16, 24, 24)
        layout.setSpacing(16)

        showcase = info.showcase_factory(container)
        layout.addWidget(showcase)
        layout.addStretch()

        self.setWidget(container)
        self._apply_style()

    def _set_placeholder(self, text: str = "Select a component from the menu.") -> None:
        """Show a centred placeholder label."""
        engine = ThemeEngine.instance()
        try:
            text_color = engine.get_token("colors", "text_secondary")
            font_size = engine.get_token("font_sizes", "medium")
        except Exception:
            text_color = "#999"
            font_size = 14

        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {text_color}; font-size: {font_size}px;")
        layout.addWidget(label)
        self.setWidget(placeholder)

    def _on_theme_changed(self, _theme_name: str) -> None:
        """Slot: refresh background when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware background from GalleryStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(GalleryStyles.showcase_panel_style(theme))
