"""TTag atom component: a label tag with size, color type, and closable support.

Supports Small/Medium/Large sizes and Default/Primary/Success/Warning/Error
color types. Optionally displays a close button that emits ``closed``.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


class TTag(BaseWidget):
    """Tag component for displaying categorised labels or status markers.

    Args:
        text: Tag label text.
        tag_type: Color type variant.
        size: Size variant.
        closable: Whether to show a close button.
        parent: Optional parent widget.

    Signals:
        closed: Emitted when the close button is clicked.

    Example:
        >>> tag = TTag("New", tag_type=TTag.TagType.PRIMARY, closable=True)
        >>> tag.closed.connect(lambda: print("tag closed"))
    """

    class TagSize(str, Enum):
        """Size variants for TTag."""

        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class TagType(str, Enum):
        """Color type variants for TTag."""

        DEFAULT = "default"
        PRIMARY = "primary"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    closed = Signal()

    def __init__(
        self,
        text: str = "",
        tag_type: TagType = TagType.DEFAULT,
        size: TagSize = TagSize.MEDIUM,
        closable: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._tag_type = tag_type
        self._size = size
        self._closable = closable
        self._text = text

        # Layout: [label] [close_btn?]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._label = QLabel(text, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)

        self._close_btn: QPushButton | None = None
        if closable:
            self._close_btn = QPushButton("\u2715", self)  # Unicode multiplication sign as close icon
            self._close_btn.setObjectName("tag_close_btn")
            self._close_btn.setFixedSize(QSize(16, 16))
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self.closed.emit)
            self._layout.addWidget(self._close_btn)

        # Dynamic properties for QSS selectors
        self.setProperty("tagType", tag_type.value)
        self.setProperty("tagSize", size.value)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.apply_theme()

    # -- Public API --

    @property
    def tag_type(self) -> TagType:
        """Return the current color type."""
        return self._tag_type

    @property
    def size(self) -> TagSize:
        """Return the current size variant."""
        return self._size

    @property
    def text(self) -> str:
        """Return the tag label text."""
        return self._text

    @property
    def closable(self) -> bool:
        """Return whether the tag has a close button."""
        return self._closable

    def set_text(self, text: str) -> None:
        """Update the tag label text.

        Args:
            text: New label string.
        """
        self._text = text
        self._label.setText(text)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this tag."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("tag.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(60, 24)
