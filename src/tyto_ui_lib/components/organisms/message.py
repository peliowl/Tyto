"""TMessage organism component and MessageManager singleton.

Provides global toast-style messages that appear from the top of the screen,
stack vertically, and auto-dismiss after a configurable duration.  Supports
Info, Success, Warning, and Error types with distinct icons and colors.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSize,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


class MessageType(str, Enum):
    """Message severity types."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


# Unicode icons per message type
_ICONS: dict[MessageType, str] = {
    MessageType.INFO: "\u2139",      # ℹ
    MessageType.SUCCESS: "\u2714",   # ✔
    MessageType.WARNING: "\u26A0",   # ⚠
    MessageType.ERROR: "\u2716",     # ✖
}


# Fixed spacing between stacked messages (px)
_MESSAGE_GAP = 10
# Top margin from screen edge (px)
_TOP_MARGIN = 20


class TMessage(BaseWidget):
    """Single message bubble widget.

    Displays a type-specific icon and text label.  Intended to be managed
    by ``MessageManager`` rather than created directly.

    Args:
        text: Message content string.
        msg_type: Severity type (Info, Success, Warning, Error).
        duration: Auto-dismiss delay in milliseconds (0 = no auto-dismiss).
        parent: Optional parent widget.

    Signals:
        closed: Emitted when the message finishes its close animation.

    Example:
        >>> msg = TMessage("Saved!", msg_type=MessageType.SUCCESS, parent=window)
        >>> msg.show_message()
    """

    closed = Signal()

    def __init__(
        self,
        text: str,
        msg_type: MessageType = MessageType.INFO,
        duration: int = 3000,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._msg_type = msg_type
        self._duration = duration
        self._text = text

        # Frameless, always-on-top within parent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Layout: [icon] [text]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._icon_label = QLabel(_ICONS.get(msg_type, ""), self)
        self._icon_label.setObjectName("message_icon")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._icon_label)

        self._text_label = QLabel(text, self)
        self._text_label.setObjectName("message_text")
        self._text_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self._layout.addWidget(self._text_label, 1)

        # Dynamic property for QSS selectors
        self.setProperty("messageType", msg_type.value)

        # Auto-dismiss timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        if duration > 0:
            self._timer.setInterval(duration)
            self._timer.timeout.connect(self.close_message)

        self.apply_theme()

    # -- Public API --

    @property
    def msg_type(self) -> MessageType:
        """Return the message severity type."""
        return self._msg_type

    @property
    def duration(self) -> int:
        """Return the auto-dismiss duration in milliseconds."""
        return self._duration

    @property
    def text(self) -> str:
        """Return the message text."""
        return self._text

    def show_message(self) -> None:
        """Show the message with a slide-down animation and start the timer."""
        self.show()
        self.raise_()

        # Slide-in from above
        start_y = self.y() - self.height()
        end_y = self.y()

        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(250)
        anim.setStartValue(QPoint(self.x(), start_y))
        anim.setEndValue(QPoint(self.x(), end_y))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

        if self._duration > 0:
            self._timer.start()

    def close_message(self) -> None:
        """Close the message with a fade-up animation and emit ``closed``."""
        self._timer.stop()

        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(200)
        anim.setStartValue(self.pos())
        anim.setEndValue(QPoint(self.x(), self.y() - self.height()))
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self._on_close_finished)
        anim.start()

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this message."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("message.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(300, 40)

    # -- Private --

    def _on_close_finished(self) -> None:
        """Handle animation completion: hide, emit closed, schedule deletion."""
        self.hide()
        self.closed.emit()
        self.deleteLater()



@dataclass
class MessageSlot:
    """Position information for a message in the stack.

    Attributes:
        message: The TMessage widget instance.
        y_offset: Vertical offset from the top of the parent window.
        created_at: Timestamp when the message was created.
    """

    message: TMessage
    y_offset: int = 0
    created_at: float = field(default_factory=time.time)


class MessageManager:
    """Global message manager (singleton) that handles message stacking.

    Creates TMessage instances, positions them at the top-centre of the
    active window, and recalculates positions when messages are added or
    removed.

    Example:
        >>> MessageManager.info("Operation completed")
        >>> MessageManager.error("Something went wrong", duration=5000)
    """

    _instance: ClassVar[MessageManager | None] = None
    _slots: ClassVar[list[MessageSlot]] = []

    @classmethod
    def instance(cls) -> MessageManager:
        """Return the singleton MessageManager, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton. Primarily for testing."""
        cls._slots.clear()
        cls._instance = None

    @classmethod
    def info(cls, text: str, duration: int = 3000) -> TMessage:
        """Show an info message.

        Args:
            text: Message content.
            duration: Auto-dismiss delay in ms.

        Returns:
            The created TMessage instance.
        """
        return cls.instance()._show(text, MessageType.INFO, duration)

    @classmethod
    def success(cls, text: str, duration: int = 3000) -> TMessage:
        """Show a success message.

        Args:
            text: Message content.
            duration: Auto-dismiss delay in ms.

        Returns:
            The created TMessage instance.
        """
        return cls.instance()._show(text, MessageType.SUCCESS, duration)

    @classmethod
    def warning(cls, text: str, duration: int = 3000) -> TMessage:
        """Show a warning message.

        Args:
            text: Message content.
            duration: Auto-dismiss delay in ms.

        Returns:
            The created TMessage instance.
        """
        return cls.instance()._show(text, MessageType.WARNING, duration)

    @classmethod
    def error(cls, text: str, duration: int = 3000) -> TMessage:
        """Show an error message.

        Args:
            text: Message content.
            duration: Auto-dismiss delay in ms.

        Returns:
            The created TMessage instance.
        """
        return cls.instance()._show(text, MessageType.ERROR, duration)

    @classmethod
    def active_slots(cls) -> list[MessageSlot]:
        """Return a copy of the current message slots (for testing)."""
        return list(cls._slots)

    # -- Private --

    def _show(self, text: str, msg_type: MessageType, duration: int) -> TMessage:
        """Create, position, and show a message.

        Args:
            text: Message content.
            msg_type: Severity type.
            duration: Auto-dismiss delay in ms.

        Returns:
            The created TMessage instance.
        """
        app = QApplication.instance()
        parent: QWidget | None = None
        if app is not None:
            parent = app.activeWindow()

        msg = TMessage(text, msg_type=msg_type, duration=duration, parent=parent)
        msg.adjustSize()

        slot = MessageSlot(message=msg, created_at=time.time())
        self._slots.append(slot)

        self._update_positions()
        msg.closed.connect(lambda: self._remove(slot))
        msg.show_message()
        return msg

    def _remove(self, slot: MessageSlot) -> None:
        """Remove a slot and recalculate positions.

        Args:
            slot: The MessageSlot to remove.
        """
        if slot in self._slots:
            self._slots.remove(slot)
            self._update_positions()

    def _update_positions(self) -> None:
        """Recalculate y_offset for all visible messages.

        Messages are stacked top-to-bottom in creation order with a fixed
        gap between them.  Each message is horizontally centred relative
        to its parent window (using global coordinates since TMessage is a
        top-level Tool window).
        """
        y = _TOP_MARGIN
        for slot in self._slots:
            msg = slot.message
            slot.y_offset = y

            # Horizontal centre relative to parent window (global coords)
            parent = msg.parentWidget()
            if parent is not None:
                parent_global = parent.mapToGlobal(QPoint(0, 0))
                cx = parent_global.x() + (parent.width() - msg.width()) // 2
                cy = parent_global.y() + y
            else:
                screen = QApplication.primaryScreen()
                if screen is not None:
                    cx = (screen.availableGeometry().width() - msg.width()) // 2
                else:
                    cx = 100
                cy = y

            msg.move(cx, cy)
            y += msg.sizeHint().height() + _MESSAGE_GAP
