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
from tyto_ui_lib.core.event_bus import EventBus

# All known component event names for EventBus subscription
_ALL_COMPONENT_EVENTS: list[str] = [
    # Atoms
    "TButton:clicked",
    "TButton:focus_in", "TButton:focus_out",
    "TInput:text_changed", "TInput:cleared", "TInput:input", "TInput:focus", "TInput:blur",
    "TInput:click", "TInput:mousedown", "TInput:keydown", "TInput:keyup",
    "TCheckbox:state_changed",
    "TCheckbox:focus_in", "TCheckbox:focus_out",
    "TCheckboxGroup:value_changed",
    "TRadio:toggled",
    "TRadio:focus_in", "TRadio:focus_out",
    "TRadioButton:toggled",
    "TRadioGroup:selection_changed",
    "TSwitch:toggled",
    "TSwitch:focus_in", "TSwitch:focus_out",
    "TTag:closed", "TTag:checked_changed", "TTag:mouse_enter", "TTag:mouse_leave",
    "TInputNumber:value_changed", "TInputNumber:focused", "TInputNumber:blurred", "TInputNumber:cleared",
    "TInputNumber:wheel",
    "TSlider:value_changed", "TSlider:drag_start", "TSlider:drag_end",
    "TSlider:focus_in", "TSlider:focus_out", "TSlider:wheel",
    "TSpin:spinning_changed",
    "TBackTop:clicked", "TBackTop:visibility_changed", "TBackTop:shown", "TBackTop:hidden",
    # Molecules
    "TSearchBar:search_changed", "TSearchBar:search_submitted",
    "TBreadcrumb:item_clicked",
    "TAlert:closed", "TAlert:after_leave",
    "TCollapse:item_expanded", "TCollapse:item_header_clicked", "TCollapse:expanded_names_changed",
    "TPopconfirm:confirmed", "TPopconfirm:cancelled",
    "TTimeline:item_clicked",
    "TTimelineItem:clicked",
    # Organisms
    "TMessage:closed", "TMessage:leave",
    "TMessage:show", "TMessage:hide",
    "TModal:closed", "TModal:esc_pressed", "TModal:mask_clicked",
    "TModal:after_enter", "TModal:before_leave", "TModal:after_leave",
    "TModal:positive_clicked", "TModal:negative_clicked",
    "TModal:show", "TModal:hide",
    "TCard:closed",
    "TLayout:scrolled",
    "TLayoutSider:collapsed_changed", "TLayoutSider:after_enter", "TLayoutSider:after_leave", "TLayoutSider:scrolled",
    "TMenu:item_selected", "TMenu:expanded_keys_changed",
    "TMenuItem:clicked",
    "TMenuItem:mouse_enter", "TMenuItem:mouse_leave",
    "TMenuItemGroup:expanded_changed",
]


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
        self.resize(1200, 640)
        self.setMinimumSize(800, 400)

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

        # EventBus logging for event verification
        self._setup_event_bus_logging()

    def _setup_event_bus_logging(self) -> None:
        """Subscribe to all known component events on the EventBus and log to console."""
        bus = EventBus.instance()
        for event_name in _ALL_COMPONENT_EVENTS:
            bus.on(event_name, lambda *args, name=event_name: self._log_bus_event(name, *args))

    @staticmethod
    def _log_bus_event(event_name: str, source: object = None, *args: object) -> None:
        """Print event info to console for debugging.

        Args:
            event_name: The full event name (e.g. "TButton:clicked").
            source: The widget instance that emitted the event.
            *args: Additional signal arguments.
        """
        class_name = type(source).__name__ if source else "Unknown"
        print(f"[EventBus] {event_name} from {class_name} args={args}")

    def _on_theme_changed(self, _theme_name: str) -> None:
        """Slot: refresh main window background when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware background color from PlaygroundStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(PlaygroundStyles.main_window_style(theme))
