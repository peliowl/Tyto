"""ModalShowcase: demonstrates TModal features."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TButton, TModal


class ModalShowcase(BaseShowcase):
    """Showcase for the TModal organism component.

    Sections: basic usage (open/close dialog).

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Build modal (parented to the top-level window at show time)
        self._modal = TModal(title="Example Modal", closable=True, mask_closable=True)
        self._modal.set_content(QLabel("This is the modal body content."))

        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        cancel_btn = TButton("Cancel", button_type=TButton.ButtonType.DEFAULT)
        ok_btn = TButton("OK", button_type=TButton.ButtonType.PRIMARY)
        cancel_btn.clicked.connect(self._modal.close)
        ok_btn.clicked.connect(self._modal.close)
        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(ok_btn)
        self._modal.set_footer(footer)

        open_btn = TButton("Open Modal", button_type=TButton.ButtonType.PRIMARY)
        open_btn.clicked.connect(self._open_modal)

        self.add_section(
            "Basic Usage",
            "Click to open a modal dialog with mask overlay.",
            open_btn,
        )

    def _open_modal(self) -> None:
        """Open the modal, parenting it to the top-level window."""
        window = self.window()
        if window is not None:
            self._modal.setParent(window)
            self._modal.resize(window.size())
        self._modal.open()
