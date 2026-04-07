"""GalleryWindow: main window composing TopBar, NavigationMenu, and ComponentShowcase."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from examples.gallery.models.component_registry import ComponentRegistry
from examples.gallery.showcases import register_all
from examples.gallery.styles.gallery_styles import GalleryStyles
from examples.gallery.viewmodels.gallery_viewmodel import GalleryViewModel
from examples.gallery.views.component_showcase import ComponentShowcase
from examples.gallery.views.navigation_menu import NavigationMenu
from examples.gallery.views.top_bar import TopBar
from tyto_ui_lib import ThemeEngine


class GalleryWindow(QWidget):
    """Main gallery window composing TopBar, NavigationMenu, and ComponentShowcase.

    Initialises the MVVM stack (Registry → ViewModel → Views), registers
    all component showcases, and wires the signal flow so that clicking a
    navigation item updates the showcase panel.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tyto UI Gallery")
        self.resize(1000, 720)

        # -- Core setup --
        engine = ThemeEngine.instance()
        engine.load_tokens()
        engine.switch_theme("light")

        # -- MVVM wiring --
        registry = ComponentRegistry()
        register_all(registry)
        self._viewmodel = GalleryViewModel(registry)

        # -- Views --
        self._top_bar = TopBar(self._viewmodel)
        self._nav_menu = NavigationMenu(self._viewmodel)
        self._showcase = ComponentShowcase(self._viewmodel)

        # -- Layout: TopBar on top, Nav left + Showcase right --
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._top_bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._nav_menu)
        body.addWidget(self._showcase, 1)  # showcase stretches
        root.addLayout(body, 1)

        # -- Signal connections --
        # Nav click → ViewModel → Showcase + Nav highlight
        self._nav_menu.component_selected.connect(self._viewmodel.select_component)
        self._viewmodel.current_component_changed.connect(self._showcase.show_component)
        self._viewmodel.current_component_changed.connect(self._nav_menu.set_active_item)

        # Theme change → update main window background
        engine.theme_changed.connect(self._on_theme_changed)
        self._apply_style()

    def _on_theme_changed(self, _theme_name: str) -> None:
        """Slot: refresh main window background when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware background color from GalleryStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(GalleryStyles.main_window_style(theme))
