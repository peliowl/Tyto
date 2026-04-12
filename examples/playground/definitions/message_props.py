"""Property definitions for TMessage / MessageManager in the Playground."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import MessageManager, MessageType, TButton


class _MessageDemo(QWidget):
    """Wrapper widget that provides buttons to trigger each message type."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._duration = 3000
        self._text = "This is a message"

        for mt in MessageType:
            btn = TButton(mt.value.capitalize(), button_type=TButton.ButtonType.DEFAULT)
            btn.clicked.connect(self._make_trigger(mt))
            layout.addWidget(btn)

    def _make_trigger(self, mt: MessageType):  # noqa: ANN202
        """Return a slot that fires a message of the given type."""
        def _trigger() -> None:
            getattr(MessageManager, mt.value)(self._text, self._duration)
        return _trigger

    def set_duration(self, value: int) -> None:
        """Update the duration used for subsequent messages."""
        self._duration = max(0, value)

    def set_text(self, value: str) -> None:
        """Update the text used for subsequent messages."""
        self._text = value


def register(registry: PropertyRegistry) -> None:
    """Register TMessage property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="text", label="Text", prop_type="str", default="This is a message",
            apply=lambda w, v: w.set_text(str(v)),
        ),
        PropertyDefinition(
            name="duration", label="Duration (ms)", prop_type="int", default=3000,
            apply=lambda w, v: w.set_duration(int(v)),
        ),
    ]

    registry.register("message", definitions)
    registry.register_factory("message", lambda: _MessageDemo())
