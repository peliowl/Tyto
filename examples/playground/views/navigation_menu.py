"""NavigationMenu view: left sidebar with categorised component list for the Playground."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from examples.playground.styles.playground_styles import PlaygroundStyles
from examples.playground.viewmodels.playground_viewmodel import PlaygroundViewModel
from tyto_ui_lib import ThemeEngine

# Human-readable category titles.
_CATEGORY_TITLES: dict[str, str] = {
    "atoms": "Atoms",
    "molecules": "Molecules",
    "organisms": "Organisms",
}


class NavigationMenu(QWidget):
    """Left sidebar navigation with categorised component list.

    The menu is built dynamically from the ``ComponentRegistry`` held by
    the view-model.  Clicking an item emits ``component_selected`` and
    highlights the active entry.

    Args:
        viewmodel: Playground view-model providing the registry.
        parent: Optional parent widget.

    Signals:
        component_selected: Emitted with the component *key* on click.
    """

    component_selected = Signal(str)

    def __init__(self, viewmodel: PlaygroundViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("nav_menu")
        self.setFixedWidth(220)
        self._viewmodel = viewmodel
        self._buttons: dict[str, QPushButton] = {}
        self._active_key: str | None = None

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Wrap menu content in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setObjectName("nav_scroll_area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_content.setObjectName("nav_scroll_content")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        registry = viewmodel.get_component_registry()
        for category in registry.categories():
            # Category header
            header = QLabel(_CATEGORY_TITLES.get(category, category.title()))
            header.setProperty("class", "nav_category")
            layout.addWidget(header)

            # Component items
            for info in registry.get_by_category(category):
                btn = QPushButton(info.name)
                btn.setProperty("class", "nav_item")
                btn.setProperty("active", False)
                btn.setCursor(self.cursor())
                btn.clicked.connect(self._make_click_handler(info.key))
                layout.addWidget(btn)
                self._buttons[info.key] = btn

        layout.addStretch()

        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)

        # Apply initial style and listen for theme changes
        self._apply_style()
        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._on_theme_changed)

    def _make_click_handler(self, key: str):  # noqa: ANN202
        """Return a slot that emits component_selected for *key*."""
        def handler() -> None:
            self.component_selected.emit(key)
        return handler

    def set_active_item(self, key: str) -> None:
        """Highlight *key* and de-highlight the previous selection."""
        if self._active_key and self._active_key in self._buttons:
            old = self._buttons[self._active_key]
            old.setProperty("active", False)
            old.style().unpolish(old)
            old.style().polish(old)

        self._active_key = key
        if key in self._buttons:
            btn = self._buttons[key]
            btn.setProperty("active", True)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Slot: refresh QSS when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware QSS from PlaygroundStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(PlaygroundStyles.nav_menu_style(theme))
