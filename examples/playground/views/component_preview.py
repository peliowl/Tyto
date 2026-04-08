"""ComponentPreview view: center panel displaying a live component instance."""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from examples.playground.styles.playground_styles import PlaygroundStyles
from examples.playground.viewmodels.playground_viewmodel import PlaygroundViewModel
from tyto_ui_lib import ThemeEngine

logger = logging.getLogger(__name__)


class ComponentPreview(QScrollArea):
    """Center panel displaying a live component instance.

    Creates a default instance of the selected component via the factory
    registered in :class:`PropertyRegistry` and updates its properties
    in real-time when the property panel changes values.

    Args:
        viewmodel: Playground view-model providing registries.
        parent: Optional parent widget.
    """

    def __init__(self, viewmodel: PlaygroundViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("preview_panel")
        self._viewmodel = viewmodel
        self._current_widget: QWidget | None = None
        self._current_key: str | None = None

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Start with an empty placeholder
        self._set_placeholder()

        # Apply initial style and listen for theme changes
        self._apply_style()
        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._on_theme_changed)

    def show_component(self, key: str) -> None:
        """Create a default instance of the component and display it.

        Uses the factory registered in :class:`PropertyRegistry` for *key*.
        Falls back to a placeholder message if no factory is found.

        Args:
            key: Registered component key (e.g. ``"button"``).
        """
        prop_registry = self._viewmodel.get_property_registry()
        factory = prop_registry.get_factory(key)
        if factory is None:
            self._set_placeholder(f"No preview factory for '{key}'.")
            self._current_widget = None
            self._current_key = None
            return

        try:
            widget = factory()
        except Exception:
            logger.exception("Failed to create component instance for '%s'", key)
            self._set_placeholder(f"Error creating '{key}' instance.")
            self._current_widget = None
            self._current_key = None
            return

        self._current_widget = widget
        self._current_key = key

        # Store back-reference so apply callbacks can update _current_widget
        widget._preview_owner = self

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(widget)
        layout.addStretch()

        self.setWidget(container)
        self._apply_style()

    def update_property(self, name: str, value: Any) -> None:
        """Apply a property change to the current component instance.

        Looks up the :class:`PropertyDefinition` for *name* in the current
        component's definitions and invokes its ``apply`` callback.

        Args:
            name: The property name to update.
            value: The new property value.
        """
        if self._current_widget is None or self._current_key is None:
            return

        prop_registry = self._viewmodel.get_property_registry()
        definitions = prop_registry.get_definitions(self._current_key)
        for prop_def in definitions:
            if prop_def.name == name and prop_def.apply is not None:
                try:
                    prop_def.apply(self._current_widget, value)
                except Exception:
                    logger.exception(
                        "Failed to apply property '%s' = %r to '%s'",
                        name, value, self._current_key,
                    )
                return

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
        """Apply theme-aware background from PlaygroundStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        self.setStyleSheet(PlaygroundStyles.preview_panel_style(theme))
