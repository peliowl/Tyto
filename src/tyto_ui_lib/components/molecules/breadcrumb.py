"""TBreadcrumb molecule component: navigation breadcrumb trail.

Renders a list of path items with separators. The last item is styled
as the current (non-clickable) location. Clicking earlier items emits
the item_clicked signal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


@dataclass
class BreadcrumbItem:
    """A single breadcrumb path entry.

    Attributes:
        label: Display text for the breadcrumb item.
        data: Arbitrary data associated with this item.
    """

    label: str
    data: Any = field(default=None)


class _ClickableLabel(QLabel):
    """Internal label that emits a signal on click."""

    clicked = Signal()

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Emit clicked on left-button press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class TBreadcrumb(BaseWidget):
    """Breadcrumb navigation component.

    Renders a horizontal list of path items separated by a configurable
    separator string. All items except the last are clickable; the last
    item represents the current location.

    Args:
        items: Initial list of breadcrumb items.
        separator: Separator string between items (default "/").
        parent: Optional parent widget.

    Signals:
        item_clicked: Emitted with (index, data) when a non-last item is clicked.

    Example:
        >>> bc = TBreadcrumb(items=[
        ...     BreadcrumbItem("Home", "/"),
        ...     BreadcrumbItem("Settings", "/settings"),
        ... ])
        >>> bc.item_clicked.connect(lambda i, d: print(f"Clicked {i}: {d}"))
    """

    item_clicked = Signal(int, object)

    def __init__(
        self,
        items: list[BreadcrumbItem] | None = None,
        separator: str = "/",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._items: list[BreadcrumbItem] = []
        self._separator = separator

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addStretch()

        if items:
            self.set_items(items)

        self.apply_theme()

    # -- Public API --

    def set_items(self, items: list[BreadcrumbItem]) -> None:
        """Replace the breadcrumb items and rebuild the UI.

        Args:
            items: New list of breadcrumb items.
        """
        self._items = list(items)
        self._rebuild()

    def get_items(self) -> list[BreadcrumbItem]:
        """Return a copy of the current breadcrumb items.

        Returns:
            List of BreadcrumbItem instances.
        """
        return list(self._items)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this breadcrumb."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("breadcrumb.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    # -- Size hint --

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(300, 28)

    # -- Private --

    def _rebuild(self) -> None:
        """Clear and recreate all child labels from the items list."""
        # Remove existing widgets
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i, item in enumerate(self._items):
            is_last = i == len(self._items) - 1

            if is_last:
                # Last item: non-clickable current location
                label = QLabel(item.label, self)
                label.setProperty("current", "true")
            else:
                # Clickable item
                label = _ClickableLabel(item.label, self)
                label.setProperty("clickable", "true")
                idx = i
                data = item.data
                label.clicked.connect(lambda _idx=idx, _data=data: self.item_clicked.emit(_idx, _data))

            self._layout.addWidget(label)

            # Add separator after non-last items
            if not is_last:
                sep = QLabel(self._separator, self)
                sep.setProperty("separator", "true")
                self._layout.addWidget(sep)

        self._layout.addStretch()
