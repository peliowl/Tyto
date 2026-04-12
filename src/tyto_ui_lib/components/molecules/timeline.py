"""TTimeline and TTimelineItem molecule components: vertical/horizontal timeline display.

Provides a timeline container (TTimeline) that manages a sequence of
TTimelineItem nodes. Each item has a status dot, title, content, and
optional time label. Supports left/right/horizontal layout modes,
custom dot/icon widgets, dashed connecting lines, and size variants.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color


# -- Status-to-token-key mapping --
_STATUS_COLOR_KEYS: dict[str, str] = {
    "default": "timeline_default",
    "pending": "timeline_pending",
    "finished": "timeline_finished",
    "error": "timeline_error",
    "success": "timeline_finished",
    "warning": "timeline_warning",
    "info": "timeline_info",
}


class TTimelineItem(BaseWidget):
    """A single timeline node with status, title, content, and time label.

    Supports custom dot/icon widget via ``set_dot()`` / ``set_icon()``,
    custom title widget via ``set_title()``, custom footer widget via
    ``set_footer()``, color override via the ``color`` property, and
    dashed connecting lines via ``line_type``.

    Args:
        title: Title text for this timeline node.
        content: Description text displayed below the title.
        time: Time label string (e.g. "2024-01-15 10:30").
        status: Node status controlling the dot color.
        color: Optional custom color string overriding the status preset.
        line_type: Connecting line type below this node.
        parent: Optional parent widget.

    Example:
        >>> item = TTimelineItem(
        ...     title="Deployed v1.0",
        ...     content="Production release",
        ...     time="2024-01-15",
        ...     status=TTimelineItem.ItemStatus.FINISHED,
        ...     line_type=TTimelineItem.LineType.DASHED,
        ... )
    """

    class ItemStatus(str, Enum):
        """Timeline item status types."""

        DEFAULT = "default"
        PENDING = "pending"
        FINISHED = "finished"
        ERROR = "error"
        SUCCESS = "success"
        WARNING = "warning"
        INFO = "info"

    class LineType(str, Enum):
        """Timeline connecting line types."""

        DEFAULT = "default"
        DASHED = "dashed"

    clicked = Signal()

    def __init__(
        self,
        title: str = "",
        content: str = "",
        time: str = "",
        status: ItemStatus = ItemStatus.DEFAULT,
        color: str | None = None,
        line_type: LineType = LineType.DEFAULT,
        parent: QWidget | None = None,
    ) -> None:
        self._title_text = title
        self._content_text = content
        self._time_text = time
        self._status = status
        self._custom_color = color
        self._custom_dot: QWidget | None = None
        self._line_type = line_type
        self._custom_title: QWidget | None = None
        self._custom_footer: QWidget | None = None

        super().__init__(parent)

        self.setProperty("itemStatus", status.value)
        self.setProperty("lineType", line_type.value)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Overall horizontal layout
        self._root_layout = QHBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        # Title row: dot + title horizontally, vertically centered
        self._title_row = QHBoxLayout()
        self._title_row.setContentsMargins(0, 0, 0, 0)
        self._title_row.setSpacing(8)

        self._dot_label = QLabel(self)
        self._dot_label.setObjectName("timeline_dot")
        self._dot_label.setFixedSize(8, 8)
        self._dot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_row.addWidget(self._dot_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self._title_label = QLabel(title, self)
        self._title_label.setObjectName("timeline_title")
        self._title_label.setWordWrap(True)
        self._title_row.addWidget(self._title_label, 1, Qt.AlignmentFlag.AlignVCenter)

        # Text column: title_row on top, then content and time below
        self._text_column = QVBoxLayout()
        self._text_column.setContentsMargins(0, 0, 0, 0)
        self._text_column.setSpacing(2)

        self._text_column.addLayout(self._title_row)

        self._content_label = QLabel(content, self)
        self._content_label.setObjectName("timeline_content")
        self._content_label.setWordWrap(True)
        # Indent content/time to align with title text (dot_width + spacing)
        self._content_label.setContentsMargins(16, 0, 0, 0)
        if not content:
            self._content_label.setVisible(False)
        self._text_column.addWidget(self._content_label)

        self._time_label = QLabel(time, self)
        self._time_label.setObjectName("timeline_time")
        self._time_label.setContentsMargins(16, 0, 0, 0)
        if not time:
            self._time_label.setVisible(False)
        self._text_column.addWidget(self._time_label)

        self._root_layout.addLayout(self._text_column, 1)

        self._apply_dot_color()
        self.apply_theme()

    # -- Public properties --

    @property
    def title(self) -> str:
        """Return the title text.

        Returns:
            The title string.
        """
        return self._title_text

    @title.setter
    def title(self, value: str) -> None:
        """Set the title text.

        Args:
            value: New title string.
        """
        self._title_text = value
        self._title_label.setText(value)

    @property
    def content(self) -> str:
        """Return the content text.

        Returns:
            The content string.
        """
        return self._content_text

    @content.setter
    def content(self, value: str) -> None:
        """Set the content text.

        Args:
            value: New content string.
        """
        self._content_text = value
        self._content_label.setText(value)
        self._content_label.setVisible(bool(value))

    @property
    def time(self) -> str:
        """Return the time label text.

        Returns:
            The time string.
        """
        return self._time_text

    @time.setter
    def time(self, value: str) -> None:
        """Set the time label text.

        Args:
            value: New time string.
        """
        self._time_text = value
        self._time_label.setText(value)
        self._time_label.setVisible(bool(value))

    @property
    def status(self) -> ItemStatus:
        """Return the item status.

        Returns:
            The current ItemStatus value.
        """
        return self._status

    @status.setter
    def status(self, value: ItemStatus) -> None:
        """Set the item status and update dot color.

        Args:
            value: New ItemStatus value.
        """
        self._status = value
        self.setProperty("itemStatus", value.value)
        self.style().unpolish(self)
        self.style().polish(self)
        self._apply_dot_color()

    @property
    def color(self) -> str | None:
        """Return the custom color override, or None.

        Returns:
            Custom color string or None if using status preset.
        """
        return self._custom_color

    @color.setter
    def color(self, value: str | None) -> None:
        """Set a custom color override for the dot.

        Args:
            value: CSS color string, or None to revert to status preset.
        """
        self._custom_color = value
        self._apply_dot_color()

    @property
    def line_type(self) -> LineType:
        """Return the connecting line type.

        Returns:
            The current LineType value.
        """
        return self._line_type

    @line_type.setter
    def line_type(self, value: LineType) -> None:
        """Set the connecting line type.

        Args:
            value: New LineType value.
        """
        self._line_type = value
        self.setProperty("lineType", value.value)
        self.style().unpolish(self)
        self.style().polish(self)
        # Trigger parent repaint to update the connecting line
        if self.parentWidget():
            self.parentWidget().update()

    def set_line_type(self, line_type: LineType) -> None:
        """Set the connecting line type (method form).

        Args:
            line_type: New LineType value.
        """
        self.line_type = line_type

    def set_dot(self, widget: QWidget) -> None:
        """Replace the default dot with a custom widget.

        Args:
            widget: The widget to use as the timeline dot.
        """
        # Remove old dot from title row
        if self._custom_dot is not None:
            self._title_row.removeWidget(self._custom_dot)
            self._custom_dot.setParent(None)  # type: ignore[call-overload]
            self._custom_dot = None
        else:
            self._title_row.removeWidget(self._dot_label)
            self._dot_label.setVisible(False)

        self._custom_dot = widget
        widget.setObjectName("timeline_dot")
        self._title_row.insertWidget(0, widget, 0, Qt.AlignmentFlag.AlignVCenter)

    def set_icon(self, widget: QWidget | None) -> None:
        """Replace the default dot with a custom icon widget.

        Alias for ``set_dot()`` for API consistency with NaiveUI.
        Pass None to restore the default dot.

        Args:
            widget: The widget to use as the timeline icon, or None to restore default.
        """
        if widget is None:
            # Restore default dot
            if self._custom_dot is not None:
                self._title_row.removeWidget(self._custom_dot)
                self._custom_dot.setParent(None)  # type: ignore[call-overload]
                self._custom_dot = None
                self._dot_label.setVisible(True)
                self._title_row.insertWidget(0, self._dot_label, 0, Qt.AlignmentFlag.AlignVCenter)
                self._apply_dot_color()
        else:
            self.set_dot(widget)

    def set_title(self, widget: QWidget | None) -> None:
        """Replace the default title label with a custom widget.

        Pass None to restore the default title label.

        Args:
            widget: The widget to use as the title, or None to restore default.
        """
        if widget is None:
            # Restore default title label
            if self._custom_title is not None:
                self._title_row.removeWidget(self._custom_title)
                self._custom_title.setParent(None)  # type: ignore[call-overload]
                self._custom_title = None
                self._title_label.setVisible(True)
                self._title_row.addWidget(self._title_label, 1, Qt.AlignmentFlag.AlignVCenter)
        else:
            # Hide default title and insert custom widget
            if self._custom_title is not None:
                self._title_row.removeWidget(self._custom_title)
                self._custom_title.setParent(None)  # type: ignore[call-overload]
            else:
                self._title_row.removeWidget(self._title_label)
                self._title_label.setVisible(False)
            self._custom_title = widget
            widget.setObjectName("timeline_title")
            self._title_row.addWidget(widget, 1, Qt.AlignmentFlag.AlignVCenter)

    def set_footer(self, widget: QWidget | None) -> None:
        """Set or remove a custom footer widget below the content area.

        Args:
            widget: The widget to display as footer, or None to remove.
        """
        if self._custom_footer is not None:
            self._text_column.removeWidget(self._custom_footer)
            self._custom_footer.setParent(None)  # type: ignore[call-overload]
            self._custom_footer = None

        if widget is not None:
            self._custom_footer = widget
            widget.setContentsMargins(16, 0, 0, 0)
            self._text_column.addWidget(widget)

    def get_resolved_color(self) -> str:
        """Return the effective dot color (custom or status-based).

        Returns:
            CSS color string for the dot.
        """
        if self._custom_color:
            return self._custom_color
        engine = ThemeEngine.instance()
        if engine.current_theme():
            token_key = _STATUS_COLOR_KEYS.get(self._status.value, "timeline_default")
            try:
                return str(engine.get_token("colors", token_key))
            except (RuntimeError, KeyError):
                pass
        # Fallback defaults
        fallback: dict[str, str] = {
            "default": "#d1d5db",
            "pending": "#2080f0",
            "finished": "#18a058",
            "error": "#d03050",
            "success": "#18a058",
            "warning": "#f0a020",
            "info": "#2080f0",
        }
        return fallback.get(self._status.value, "#d1d5db")

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this timeline item."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("timeline.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass
        self._apply_dot_color()

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Emit clicked signal on left-button press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    # -- Private --

    def _apply_dot_color(self) -> None:
        """Apply the resolved color to the default dot label."""
        if self._custom_dot is not None:
            return
        if not hasattr(self, "_dot_label"):
            return
        color = self.get_resolved_color()
        self._dot_label.setStyleSheet(
            f"background-color: {color}; border-radius: 4px;"
            f" min-width: 8px; min-height: 8px; max-width: 8px; max-height: 8px;"
        )

    def _set_horizontal(self, horizontal: bool) -> None:
        """Rebuild internal layout for horizontal or vertical timeline mode.

        In horizontal mode the dot is centered on top with text below.
        In vertical mode the dot is to the left of the title with text indented below.

        Args:
            horizontal: True for horizontal layout, False for vertical.
        """
        # Detach all widgets from layouts without deleting them
        for w in (self._dot_label, self._title_label, self._content_label, self._time_label):
            w.setParent(None)  # type: ignore[call-overload]
        if self._custom_dot is not None:
            self._custom_dot.setParent(None)  # type: ignore[call-overload]
        if self._custom_title is not None:
            self._custom_title.setParent(None)  # type: ignore[call-overload]
        if self._custom_footer is not None:
            self._custom_footer.setParent(None)  # type: ignore[call-overload]

        # Remove old sub-layouts from root
        while self._root_layout.count():
            child = self._root_layout.takeAt(0)
            if child.layout():
                sub = child.layout()
                while sub.count():
                    sub.takeAt(0)

        dot_widget = self._custom_dot if self._custom_dot else self._dot_label
        title_widget = self._custom_title if self._custom_title else self._title_label

        if horizontal:
            # Vertical column: dot centered on top, then title, content, time
            col = QVBoxLayout()
            col.setContentsMargins(0, 0, 0, 0)
            col.setSpacing(4)

            dot_widget.setParent(self)
            col.addWidget(dot_widget, 0, Qt.AlignmentFlag.AlignLeft)

            title_widget.setParent(self)
            col.addWidget(title_widget)

            self._content_label.setParent(self)
            self._content_label.setContentsMargins(0, 0, 0, 0)
            col.addWidget(self._content_label)

            self._time_label.setParent(self)
            self._time_label.setContentsMargins(0, 0, 0, 0)
            col.addWidget(self._time_label)

            if self._custom_footer is not None:
                self._custom_footer.setParent(self)
                col.addWidget(self._custom_footer)

            self._root_layout.addLayout(col, 1)

            self._title_row = QHBoxLayout()
            self._title_row.setContentsMargins(0, 0, 0, 0)
            self._title_row.setSpacing(8)

            self._text_column = col
        else:
            # Restore vertical mode: dot + title in a row, content/time indented below
            self._title_row = QHBoxLayout()
            self._title_row.setContentsMargins(0, 0, 0, 0)
            self._title_row.setSpacing(8)

            dot_widget.setParent(self)
            self._title_row.addWidget(dot_widget, 0, Qt.AlignmentFlag.AlignVCenter)

            title_widget.setParent(self)
            self._title_row.addWidget(title_widget, 1, Qt.AlignmentFlag.AlignVCenter)

            self._text_column = QVBoxLayout()
            self._text_column.setContentsMargins(0, 0, 0, 0)
            self._text_column.setSpacing(2)
            self._text_column.addLayout(self._title_row)

            self._content_label.setParent(self)
            self._content_label.setContentsMargins(16, 0, 0, 0)
            self._text_column.addWidget(self._content_label)

            self._time_label.setParent(self)
            self._time_label.setContentsMargins(16, 0, 0, 0)
            self._text_column.addWidget(self._time_label)

            if self._custom_footer is not None:
                self._custom_footer.setParent(self)
                self._text_column.addWidget(self._custom_footer)

            self._root_layout.addLayout(self._text_column, 1)



class TTimeline(BaseWidget):
    """Timeline component displaying a sequence of TTimelineItem nodes.

    Draws connecting lines between adjacent nodes with colors following
    the upper node's color. Supports left, right, and horizontal layout
    modes, size variants, and configurable icon size.

    Args:
        mode: Layout mode controlling content placement relative to the
            timeline axis.
        horizontal: If True, items are arranged horizontally left-to-right.
        size: Timeline size variant (medium or large).
        icon_size: Custom icon/dot size in pixels.
        parent: Optional parent widget.

    Signals:
        item_clicked: Emitted with the item index when a timeline item
            is clicked.

    Example:
        >>> timeline = TTimeline(mode=TTimeline.TimelineMode.LEFT)
        >>> timeline.add_item(TTimelineItem(title="Step 1", status=TTimelineItem.ItemStatus.FINISHED))
        >>> timeline.add_item(TTimelineItem(title="Step 2", status=TTimelineItem.ItemStatus.PENDING))
        >>> timeline.item_clicked.connect(lambda idx: print(f"Clicked item {idx}"))
    """

    class TimelineMode(str, Enum):
        """Timeline layout modes."""

        LEFT = "left"
        RIGHT = "right"

    class TimelineSize(str, Enum):
        """Timeline size variants."""

        MEDIUM = "medium"
        LARGE = "large"

    item_clicked = Signal(int)

    # Spacing between items and line drawing constants
    _ITEM_SPACING = 16
    _DOT_SIZE = 8
    _LINE_WIDTH = 2

    def __init__(
        self,
        mode: TimelineMode = TimelineMode.LEFT,
        horizontal: bool = False,
        size: TimelineSize = TimelineSize.MEDIUM,
        icon_size: int = 12,
        parent: QWidget | None = None,
    ) -> None:
        self._mode = mode
        self._horizontal = horizontal
        self._size = size
        self._icon_size = icon_size
        self._items: list[TTimelineItem] = []

        super().__init__(parent)

        self.setProperty("timelineSize", size.value)
        self.setProperty("horizontal", str(horizontal).lower())

        if horizontal:
            self._items_layout = QHBoxLayout(self)
        else:
            self._items_layout = QVBoxLayout(self)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(self._ITEM_SPACING)
        self._items_layout.addStretch()

        self.apply_theme()

    # -- Public API --

    @property
    def mode(self) -> TimelineMode:
        """Return the current layout mode.

        Returns:
            The TimelineMode value.
        """
        return self._mode

    @mode.setter
    def mode(self, value: TimelineMode) -> None:
        """Set the layout mode and rebuild the layout.

        Args:
            value: New TimelineMode value.
        """
        self._mode = value
        self._rebuild_layout()

    @property
    def horizontal(self) -> bool:
        """Return whether the timeline is in horizontal mode.

        Returns:
            True if horizontal, False if vertical.
        """
        return self._horizontal

    @horizontal.setter
    def horizontal(self, value: bool) -> None:
        """Set horizontal mode and rebuild the layout.

        Args:
            value: True for horizontal, False for vertical.
        """
        if self._horizontal == value:
            return
        self._horizontal = value
        self.setProperty("horizontal", str(value).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self._rebuild_full_layout()

    def set_horizontal(self, horizontal: bool) -> None:
        """Set horizontal mode (method form).

        Args:
            horizontal: True for horizontal, False for vertical.
        """
        self.horizontal = horizontal

    @property
    def size(self) -> TimelineSize:
        """Return the current size variant.

        Returns:
            The TimelineSize value.
        """
        return self._size

    @size.setter
    def size(self, value: TimelineSize) -> None:
        """Set the size variant.

        Args:
            value: New TimelineSize value.
        """
        self._size = value
        self.setProperty("timelineSize", value.value)
        self.style().unpolish(self)
        self.style().polish(self)
        # Re-polish all items and their child labels so QSS selectors take effect
        for item in self._items:
            item.style().unpolish(item)
            item.style().polish(item)
            for label in (item._title_label, item._content_label, item._time_label):
                label.style().unpolish(label)
                label.style().polish(label)
        self.update()

    def set_size(self, size: TimelineSize) -> None:
        """Set the size variant (method form).

        Args:
            size: New TimelineSize value.
        """
        self.size = size

    @property
    def icon_size(self) -> int:
        """Return the custom icon/dot size in pixels.

        Returns:
            The icon size value.
        """
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value: int) -> None:
        """Set the custom icon/dot size and update all items.

        Args:
            value: New icon size in pixels.
        """
        self._icon_size = value
        self._apply_icon_size_to_items()
        self.update()

    def set_icon_size(self, size: int) -> None:
        """Set the custom icon/dot size (method form).

        Args:
            size: New icon size in pixels.
        """
        self.icon_size = size

    def add_item(self, item: TTimelineItem) -> None:
        """Append a timeline item and connect its clicked signal.

        Args:
            item: The TTimelineItem to add.
        """
        idx = len(self._items)
        self._items.append(item)
        item.setParent(self)

        # Connect clicked signal with captured index
        item.clicked.connect(lambda _idx=idx: self.item_clicked.emit(_idx))

        # Apply icon size to the new item
        self._apply_icon_size_to_item(item)

        # Insert before the trailing stretch
        stretch_idx = self._items_layout.count() - 1
        self._items_layout.insertWidget(stretch_idx, item)

        self._apply_mode_to_item(item, idx)
        # Re-polish so parent QSS selectors (e.g. timelineSize) apply
        item.style().unpolish(item)
        item.style().polish(item)
        self.update()

    def get_items(self) -> list[TTimelineItem]:
        """Return a copy of the current items list.

        Returns:
            List of TTimelineItem instances in order.
        """
        return list(self._items)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this timeline."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("timeline.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass
        self.update()

    # -- Size hint --

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        if self._horizontal:
            return QSize(600, 150)
        return QSize(400, 300)

    # -- Paint connecting lines --

    def paintEvent(self, event: Any) -> None:
        """Draw connecting lines between adjacent timeline item dots."""
        super().paintEvent(event)

        if len(self._items) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i in range(len(self._items) - 1):
            upper = self._items[i]
            lower = self._items[i + 1]

            if not upper.isVisible() or not lower.isVisible():
                continue

            # Resolve line color from the upper item
            line_color = parse_color(upper.get_resolved_color())

            pen = QPen(line_color, self._LINE_WIDTH)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            # Apply dashed style if the upper item has dashed line_type
            if upper.line_type == TTimelineItem.LineType.DASHED:
                pen.setStyle(Qt.PenStyle.DashLine)
                pen.setDashPattern([4.0, 4.0])
            else:
                pen.setStyle(Qt.PenStyle.SolidLine)

            painter.setPen(pen)

            # Calculate dot center positions relative to this widget
            upper_dot = self._get_dot_center(upper)
            lower_dot = self._get_dot_center(lower)

            if upper_dot is not None and lower_dot is not None:
                dot_half = self._icon_size // 2 if self._icon_size > 0 else self._DOT_SIZE // 2

                if self._horizontal:
                    # Horizontal: draw line from right of upper dot to left of lower dot
                    start = QPoint(upper_dot.x() + dot_half, upper_dot.y())
                    end = QPoint(lower_dot.x() - dot_half, lower_dot.y())
                else:
                    # Vertical: draw line from bottom of upper dot to top of lower dot
                    start = QPoint(upper_dot.x(), upper_dot.y() + dot_half)
                    end = QPoint(lower_dot.x(), lower_dot.y() - dot_half)

                painter.drawLine(start, end)

        painter.end()

    # -- Private --

    def _get_dot_center(self, item: TTimelineItem) -> QPoint | None:
        """Calculate the center position of an item's dot relative to self.

        Args:
            item: The timeline item.

        Returns:
            QPoint of the dot center, or None if not available.
        """
        dot_widget: QWidget
        if item._custom_dot is not None:
            dot_widget = item._custom_dot
        else:
            dot_widget = item._dot_label

        if not dot_widget.isVisible() and item._custom_dot is None:
            return None

        # Map dot center to timeline coordinates
        dot_center = QPoint(dot_widget.width() // 2, dot_widget.height() // 2)
        return dot_widget.mapTo(self, dot_center)

    def _apply_mode_to_item(self, item: TTimelineItem, index: int) -> None:
        """Apply layout direction to an item based on the current mode.

        Args:
            item: The timeline item to configure.
            index: The item's index in the list.
        """
        # Rebuild item internal layout for horizontal/vertical
        item._set_horizontal(self._horizontal)

        if self._horizontal:
            # In horizontal mode, text is left-aligned below the dot
            item._title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            item._content_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            item._time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            return

        title_row = item._title_row
        if title_row is None:
            return

        is_reversed = self._mode == self.TimelineMode.RIGHT

        if is_reversed:
            title_row.setDirection(QHBoxLayout.Direction.RightToLeft)
            item._title_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            item._content_label.setContentsMargins(0, 0, 16, 0)
            item._time_label.setContentsMargins(0, 0, 16, 0)
            item._content_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            item._time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            title_row.setDirection(QHBoxLayout.Direction.LeftToRight)
            item._title_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            item._content_label.setContentsMargins(16, 0, 0, 0)
            item._time_label.setContentsMargins(16, 0, 0, 0)
            item._content_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            item._time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def _apply_icon_size_to_item(self, item: TTimelineItem) -> None:
        """Apply the current icon_size to a single item's default dot.

        Args:
            item: The timeline item to update.
        """
        if item._custom_dot is not None:
            return
        sz = self._icon_size
        radius = sz // 2
        item._dot_label.setFixedSize(sz, sz)
        # Re-apply dot color with updated size
        color = item.get_resolved_color()
        item._dot_label.setStyleSheet(
            f"background-color: {color}; border-radius: {radius}px;"
            f" min-width: {sz}px; min-height: {sz}px;"
            f" max-width: {sz}px; max-height: {sz}px;"
        )

    def _apply_icon_size_to_items(self) -> None:
        """Apply the current icon_size to all items."""
        for item in self._items:
            self._apply_icon_size_to_item(item)

    def _rebuild_layout(self) -> None:
        """Re-apply mode to all items after a mode change."""
        for i, item in enumerate(self._items):
            self._apply_mode_to_item(item, i)
        self.update()

    def _rebuild_full_layout(self) -> None:
        """Rebuild the entire layout when switching between horizontal/vertical."""
        # Remove all items from the current layout
        for item in self._items:
            self._items_layout.removeWidget(item)

        # Delete old layout by transferring to a temporary widget
        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        # Create new layout
        if self._horizontal:
            self._items_layout = QHBoxLayout(self)
        else:
            self._items_layout = QVBoxLayout(self)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(self._ITEM_SPACING)

        # Re-add all items
        for i, item in enumerate(self._items):
            self._items_layout.addWidget(item)
            self._apply_mode_to_item(item, i)

        self._items_layout.addStretch()
        self.update()
