"""ViewModel managing gallery navigation state and theme switching."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from examples.gallery.models.component_registry import ComponentRegistry
from tyto_ui_lib import ThemeEngine


class GalleryViewModel(QObject):
    """Manages gallery navigation state and component switching.

    Signals:
        current_component_changed: Emitted with the component *key* when
            the user selects a different component.
        theme_changed: Emitted with ``"light"`` or ``"dark"`` after a
            theme toggle.

    Args:
        registry: The component registry to query.
        parent: Optional parent QObject.
    """

    current_component_changed = Signal(str)
    theme_changed = Signal(str)

    def __init__(self, registry: ComponentRegistry, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._registry = registry
        self._current_key: str | None = None

    def select_component(self, key: str) -> None:
        """Select a component by *key* and notify listeners.

        If *key* is not registered the request is silently ignored.
        """
        if self._registry.get_by_key(key) is None:
            return
        self._current_key = key
        self.current_component_changed.emit(key)

    def current_component_key(self) -> str | None:
        """Return the currently selected component key, or ``None``."""
        return self._current_key

    def toggle_theme(self, dark: bool) -> None:
        """Switch between light and dark themes.

        Args:
            dark: ``True`` to activate the dark theme.
        """
        theme_name = "dark" if dark else "light"
        engine = ThemeEngine.instance()
        engine.switch_theme(theme_name)
        self.theme_changed.emit(theme_name)

    def get_registry(self) -> ComponentRegistry:
        """Return the underlying component registry."""
        return self._registry
