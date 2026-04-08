"""PropertyPanel view: right panel with dynamic property editors."""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.styles.playground_styles import PlaygroundStyles
from examples.playground.viewmodels.playground_viewmodel import PlaygroundViewModel
from tyto_ui_lib import ThemeEngine

logger = logging.getLogger(__name__)


class PropertyPanel(QScrollArea):
    """Right panel with dynamic property editors for the selected component.

    Generates editor widgets (QComboBox, QCheckBox, QLineEdit, QSpinBox)
    based on :class:`PropertyDefinition` metadata.  When an editor value
    changes, :attr:`property_value_changed` is emitted so the ViewModel
    can propagate the update to the preview panel.

    Args:
        viewmodel: Playground view-model providing the property registry.
        parent: Optional parent widget.

    Signals:
        property_value_changed: Emitted with ``(property_name, new_value)``.
    """

    property_value_changed = Signal(str, object)

    def __init__(self, viewmodel: PlaygroundViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("property_panel")
        self._viewmodel = viewmodel
        self._editors: dict[str, QWidget] = {}

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setFixedWidth(280)

        # Empty placeholder initially
        self._set_placeholder()

        # Apply initial style and listen for theme changes
        self._apply_style()
        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._on_theme_changed)

    def load_properties(self, key: str) -> None:
        """Generate property editors for the given component *key*.

        Clears existing editors and creates new ones based on the
        :class:`PropertyDefinition` list from the property registry.

        Args:
            key: Registered component key (e.g. ``"button"``).
        """
        self._editors.clear()
        prop_registry = self._viewmodel.get_property_registry()
        definitions = prop_registry.get_definitions(key)

        if not definitions:
            self._set_placeholder(f"No properties for '{key}'.")
            return

        container = QWidget()
        container.setObjectName("property_panel_container")
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Title
        title = QLabel("Properties")
        title.setObjectName("property_panel_title")
        outer.addWidget(title)

        # Form layout for property rows
        form = QFormLayout()
        form.setContentsMargins(12, 8, 12, 12)
        form.setSpacing(8)

        for prop_def in definitions:
            editor = self._create_editor(prop_def)
            if editor is not None:
                self._editors[prop_def.name] = editor
                label = QLabel(prop_def.label)
                label.setProperty("class", "prop_label")
                form.addRow(label, editor)

        outer.addLayout(form)
        outer.addStretch()
        self.setWidget(container)
        self._apply_style()

    def _create_editor(self, prop_def: PropertyDefinition) -> QWidget | None:
        """Create the appropriate editor widget for a property definition.

        Args:
            prop_def: The property definition describing type and options.

        Returns:
            A QWidget editor, or ``None`` if the type is unsupported.
        """
        if prop_def.prop_type == "enum":
            return self._create_enum_editor(prop_def)
        elif prop_def.prop_type == "bool":
            return self._create_bool_editor(prop_def)
        elif prop_def.prop_type == "str":
            return self._create_str_editor(prop_def)
        elif prop_def.prop_type == "int":
            return self._create_int_editor(prop_def)
        elif prop_def.prop_type == "color":
            return self._create_color_editor(prop_def)
        elif prop_def.prop_type == "file":
            return self._create_file_editor(prop_def)
        else:
            logger.warning("Unsupported prop_type '%s' for property '%s'", prop_def.prop_type, prop_def.name)
            return None

    def _create_enum_editor(self, prop_def: PropertyDefinition) -> QComboBox:
        """Create a QComboBox for an enum property."""
        combo = QComboBox()
        if prop_def.options:
            for value, label in prop_def.options:
                combo.addItem(label, value)
            # Set default selection
            for i, (value, _label) in enumerate(prop_def.options):
                if value == prop_def.default:
                    combo.setCurrentIndex(i)
                    break

        name = prop_def.name

        def on_changed(index: int) -> None:
            data = combo.itemData(index)
            self.property_value_changed.emit(name, data)

        combo.currentIndexChanged.connect(on_changed)
        return combo

    def _create_bool_editor(self, prop_def: PropertyDefinition) -> QCheckBox:
        """Create a QCheckBox for a boolean property."""
        checkbox = QCheckBox()
        checkbox.setChecked(bool(prop_def.default))
        name = prop_def.name

        def on_toggled(checked: bool) -> None:
            self.property_value_changed.emit(name, checked)

        checkbox.toggled.connect(on_toggled)
        return checkbox

    def _create_str_editor(self, prop_def: PropertyDefinition) -> QLineEdit:
        """Create a QLineEdit for a string property."""
        line_edit = QLineEdit()
        line_edit.setText(str(prop_def.default) if prop_def.default else "")
        line_edit.setPlaceholderText(prop_def.label)
        name = prop_def.name

        def on_text_changed(text: str) -> None:
            self.property_value_changed.emit(name, text)

        line_edit.textChanged.connect(on_text_changed)
        return line_edit

    def _create_int_editor(self, prop_def: PropertyDefinition) -> QSpinBox:
        """Create a QSpinBox for an integer property."""
        spinbox = QSpinBox()
        spinbox.setRange(0, 9999)
        spinbox.setValue(int(prop_def.default) if prop_def.default is not None else 0)
        name = prop_def.name

        def on_value_changed(value: int) -> None:
            self.property_value_changed.emit(name, value)

        spinbox.valueChanged.connect(on_value_changed)
        return spinbox

    def _create_color_editor(self, prop_def: PropertyDefinition) -> QWidget:
        """Create a color picker button for a color property.

        Clicking the button opens a QColorDialog. The chosen color is
        shown as the button's background and emitted as a hex string.
        A "Clear" button resets to no custom color.
        """
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QPushButton

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        btn = QPushButton("")
        btn.setFixedSize(28, 28)
        btn.setStyleSheet("background-color: transparent; border: 1px solid #ccc; border-radius: 4px;")

        clear_btn = QPushButton("×")
        clear_btn.setFixedSize(28, 28)
        clear_btn.setToolTip("Clear color")

        layout.addWidget(btn)
        layout.addWidget(clear_btn)
        layout.addStretch()

        name = prop_def.name

        def on_pick() -> None:
            color = QColorDialog.getColor(QColor(btn.toolTip() or "#ffffff"), self, f"Pick {prop_def.label}")
            if color.isValid():
                hex_val = color.name()
                btn.setStyleSheet(f"background-color: {hex_val}; border: 1px solid #ccc; border-radius: 4px;")
                btn.setToolTip(hex_val)
                self.property_value_changed.emit(name, hex_val)

        def on_clear() -> None:
            btn.setStyleSheet("background-color: transparent; border: 1px solid #ccc; border-radius: 4px;")
            btn.setToolTip("")
            self.property_value_changed.emit(name, "")

        btn.clicked.connect(on_pick)
        clear_btn.clicked.connect(on_clear)
        return container

    def _create_file_editor(self, prop_def: PropertyDefinition) -> QWidget:
        """Create a file picker button for a file/icon property.

        Clicking the button opens a QFileDialog to select an image file.
        A small preview and the filename are shown. A "×" button clears.
        """
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QPushButton

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        preview = QPushButton("")
        preview.setFixedSize(28, 28)
        preview.setIconSize(QSize(20, 20))
        preview.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        preview.setToolTip("Click to select icon file")

        clear_btn = QPushButton("×")
        clear_btn.setFixedSize(28, 28)
        clear_btn.setToolTip("Clear icon")

        layout.addWidget(preview)
        layout.addWidget(clear_btn)
        layout.addStretch()

        name = prop_def.name

        def on_pick() -> None:
            path, _ = QFileDialog.getOpenFileName(
                self, f"Select {prop_def.label}",
                "", "Images (*.png *.svg *.ico *.jpg *.jpeg *.bmp);;All Files (*)",
            )
            if path:
                icon = QIcon(path)
                preview.setIcon(icon)
                preview.setToolTip(path)
                self.property_value_changed.emit(name, path)

        def on_clear() -> None:
            preview.setIcon(QIcon())
            preview.setToolTip("Click to select icon file")
            self.property_value_changed.emit(name, "")

        preview.clicked.connect(on_pick)
        clear_btn.clicked.connect(on_clear)
        return container

    def _set_placeholder(self, text: str = "Select a component to edit properties.") -> None:
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
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {text_color}; font-size: {font_size}px; padding: 16px;")
        layout.addWidget(label)
        layout.addStretch()
        self.setWidget(placeholder)

    def _on_theme_changed(self, _theme_name: str) -> None:
        """Slot: refresh QSS when the theme switches."""
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply theme-aware QSS from PlaygroundStyles."""
        engine = ThemeEngine.instance()
        theme = engine.current_theme() or "light"
        style = PlaygroundStyles.property_panel_style(theme)
        style += PlaygroundStyles.property_row_style(theme)
        self.setStyleSheet(style)
