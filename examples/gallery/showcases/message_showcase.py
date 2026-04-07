"""MessageShowcase: demonstrates TMessage / MessageManager."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import MessageManager, TButton


class MessageShowcase(BaseShowcase):
    """Showcase for the TMessage organism component.

    Sections: basic usage (trigger each message type).

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        btn_info = TButton("Info", button_type=TButton.ButtonType.DEFAULT)
        btn_success = TButton("Success", button_type=TButton.ButtonType.PRIMARY)
        btn_warning = TButton("Warning", button_type=TButton.ButtonType.DEFAULT)
        btn_error = TButton("Error", button_type=TButton.ButtonType.DEFAULT)

        btn_info.clicked.connect(lambda: MessageManager.info("This is an info message"))
        btn_success.clicked.connect(lambda: MessageManager.success("Operation succeeded"))
        btn_warning.clicked.connect(lambda: MessageManager.warning("Please be careful"))
        btn_error.clicked.connect(lambda: MessageManager.error("Something went wrong"))

        self.add_section(
            "Basic Usage",
            "Click buttons to trigger global toast messages.",
            self.hbox(btn_info, btn_success, btn_warning, btn_error),
        )
