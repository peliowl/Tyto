"""ViewModel managing playground navigation, property state, and theme switching."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal

from examples.gallery.models.component_registry import ComponentRegistry
from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import ThemeEngine


class PlaygroundViewModel(QObject):
    """Manages playground navigation, property state, and component updates.

    Signals:
        current_component_changed: Emitted with the component *key* when
            the user selects a different component.
        property_changed: Emitted with ``(property_name, new_value)`` when
            a property is edited in the property panel.
        theme_changed: Emitted with ``"light"`` or ``"dark"`` after a
            theme toggle.

    Args:
        component_registry: The shared component registry (reused from Gallery).
        property_registry: The property definition registry.
        parent: Optional parent QObject.
    """

    current_component_changed = Signal(str)
    property_changed = Signal(str, object)
    theme_changed = Signal(str)

    def __init__(
        self,
        component_registry: ComponentRegistry,
        property_registry: PropertyRegistry,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._component_registry = component_registry
        self._property_registry = property_registry
        self._current_key: str | None = None

    def select_component(self, key: str) -> None:
        """Select a component by *key* and notify listeners.

        If *key* is not registered the request is silently ignored.

        Args:
            key: The component key to select.
        """
        if self._component_registry.get_by_key(key) is None:
            return
        self._current_key = key
        self.current_component_changed.emit(key)

    def current_component_key(self) -> str | None:
        """Return the currently selected component key, or ``None``."""
        return self._current_key

    def update_property(self, name: str, value: Any) -> None:
        """Update a property value and emit :attr:`property_changed`.

        Args:
            name: The property name.
            value: The new property value.
        """
        self.property_changed.emit(name, value)

    def toggle_theme(self, dark: bool) -> None:
        """Switch between light and dark themes.

        Args:
            dark: ``True`` to activate the dark theme.
        """
        theme_name = "dark" if dark else "light"
        engine = ThemeEngine.instance()
        engine.switch_theme(theme_name)
        self.theme_changed.emit(theme_name)

    def get_property_definitions(self) -> list[PropertyDefinition]:
        """Return property definitions for the currently selected component."""
        if self._current_key is None:
            return []
        return self._property_registry.get_definitions(self._current_key)

    def get_component_registry(self) -> ComponentRegistry:
        """Return the underlying component registry."""
        return self._component_registry

    def get_property_registry(self) -> PropertyRegistry:
        """Return the underlying property registry."""
        return self._property_registry
