"""PlaygroundWindow: main window composing TopBar, NavigationMenu, ComponentPreview, and PropertyPanel."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from examples.gallery.models.component_registry import ComponentRegistry
from examples.gallery.showcases import register_all
from examples.playground.models.property_registry import PropertyRegistry
from examples.playground.styles.playground_styles import PlaygroundStyles
from examples.playground.viewmodels.playground_viewmodel import PlaygroundViewModel
from examples.playground.views.component_preview import ComponentPreview
from examples.playground.views.navigation_menu import NavigationMenu
from examples.playground.views.property_panel import PropertyPanel
from examples.playground.views.top_bar import TopBar
from tyto_ui_lib import ThemeEngine


class PlaygroundWindow(QWidget):
    """Main playground window: TopBar + NavigationMenu + ComponentPreview + PropertyPanel.

    Initialises the MVVM stack (ComponentRegistry + PropertyRegistry →
    ViewModel → Views), registers all components and property definitions,
    and wires the signal flow for navigation, property editing, and theme
    switching.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tyto UI Playground")
        self.resize(1200, 720)

        # -- Core setup --
        engine = ThemeEngine.instance()
        engine.load_tokens()
        engine.switch_theme("light")

        # -- Registries --
        comp_registry = ComponentRegistry()
        register_all(comp_registry)

        prop_registry = PropertyRegistry()
        # Property definitions are registered by task 41 (definitions module).
        # Import and call register_all_properties if available.
        try:
            from examples.playground.definitions import register_all_properties
            register_all_properties(prop_registry)
        except ImportError:
            pass

        # -- ViewModel --
        self._viewmodel = PlaygroundViewModel(comp_registry, prop_registry)

        # -- Views --
        self._top_bar = TopBar(self._viewmodel)
        self._nav_menu = NavigationMenu(self._viewmodel)
        self._preview = ComponentPreview(self._viewmodel)
        self._props_panel = PropertyPanel(self._viewmodel)

        # -- Layout: TopBar on top, Nav left + Preview center + Props right --
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._top_bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._nav_menu)
        body.addWidget(self._preview, 1)  # preview stretches
        body.addWidget(self._props_panel)
        root.addLayout(body, 1)

        # -- Signal connections --
        # Nav click → ViewModel
        self._nav_menu.component_selected.connect(self._viewmodel.select_component)

        # ViewModel component change → Preview + Nav highlight + Props panel
        self._viewmodel.current_component_changed.connect(self._preview.show_component)
        self._viewmodel.current_component_changed.connect(self._nav_menu.set_active_item)
        self._viewmodel.current_component_changed.connect(self._props_panel.load_properties)

        # Props panel value change → ViewModel → Preview
        self._props_panel.property_value_changed.connect(self._viewmodel.update_property)
        self._viewmodel.property_changed.connect(self._preview.update_property)

        # Theme change → update main window background
        engine.theme_changed.connect(self._on_theme_changed)
        self._apply_style()

    def _on_theme_changed(self, _theme_name: str) -> None:
        """Slot: refresh main window background when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware background color from PlaygroundStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(PlaygroundStyles.main_window_style(theme))
