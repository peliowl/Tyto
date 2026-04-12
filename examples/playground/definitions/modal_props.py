"""Property definitions for TModal in the Playground."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TButton, TModal


class _ModalDemo(QWidget):
    """Wrapper widget with a button that opens a TModal dialog."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._title = "Example Modal"
        self._closable = True
        self._mask_closable = True

        open_btn = TButton("Open Modal", button_type=TButton.ButtonType.PRIMARY)
        open_btn.clicked.connect(self._open_modal)
        layout.addWidget(open_btn)

    def _open_modal(self) -> None:
        """Create and open a modal dialog parented to the top-level window."""
        window = self.window()
        modal = TModal(
            title=self._title,
            closable=self._closable,
            mask_closable=self._mask_closable,
            parent=window,
        )
        modal.set_content(QLabel("This is the modal body content."))

        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        cancel_btn = TButton("Cancel", button_type=TButton.ButtonType.DEFAULT)
        ok_btn = TButton("OK", button_type=TButton.ButtonType.PRIMARY)
        cancel_btn.clicked.connect(modal.close)
        ok_btn.clicked.connect(modal.close)
        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(ok_btn)
        modal.set_footer(footer)

        if window is not None:
            modal.resize(window.size())
        modal.open()

    def set_title(self, value: str) -> None:
        """Update the title used for the next modal open."""
        self._title = value

    def set_closable(self, value: bool) -> None:
        """Update the closable flag used for the next modal open."""
        self._closable = bool(value)

    def set_mask_closable(self, value: bool) -> None:
        """Update the mask_closable flag used for the next modal open."""
        self._mask_closable = bool(value)


def register(registry: PropertyRegistry) -> None:
    """Register TModal property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="title", label="Title", prop_type="str", default="Example Modal",
            apply=lambda w, v: w.set_title(str(v)),
        ),
        PropertyDefinition(
            name="closable", label="Closable", prop_type="bool", default=True,
            apply=lambda w, v: w.set_closable(bool(v)),
        ),
        PropertyDefinition(
            name="mask_closable", label="Mask Closable", prop_type="bool", default=True,
            apply=lambda w, v: w.set_mask_closable(bool(v)),
        ),
    ]

    registry.register("modal", definitions)
    registry.register_factory("modal", lambda: _ModalDemo())
