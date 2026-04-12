"""TCollapse and TCollapseItem molecule components: accordion-style panels.

Provides a collapsible panel container (TCollapse) that manages a set of
TCollapseItem children. Each item has a clickable header that toggles
the visibility of its content area with a smooth animated transition.
Supports accordion mode, initial expanded state, per-item disable,
arrow placement, trigger area control, and custom header content.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPalette,
    QTransform,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine

_DEFAULT_TRIGGER_AREAS: list[str] = ["main", "extra", "arrow"]

# NaiveUI ChevronRight SVG path (viewBox 0 0 16 16)
_CHEVRON_PATH_DATA = (
    "M5.64645 3.14645C5.45118 3.34171 5.45118 3.65829 5.64645 3.85355"
    "L9.79289 8L5.64645 12.1464C5.45118 12.3417 5.45118 12.6583 5.64645 12.8536"
    "C5.84171 13.0488 6.15829 13.0488 6.35355 12.8536L10.8536 8.35355"
    "C11.0488 8.15829 11.0488 7.84171 10.8536 7.64645L6.35355 3.14645"
    "C6.15829 2.95118 5.84171 2.95118 5.64645 3.14645Z"
)
_CHEVRON_VIEWBOX = 16.0


def _parse_svg_path(data: str) -> QPainterPath:
    """Parse a simplified SVG path string into a QPainterPath.

    Supports M, L, C, Z commands (absolute only) as used by the
    NaiveUI ChevronRight icon.
    """
    path = QPainterPath()
    tokens: list[str] = []
    current = ""
    for ch in data:
        if ch in "MLCZmlcz":
            if current.strip():
                tokens.append(current.strip())
            tokens.append(ch)
            current = ""
        elif ch in ", \t\n":
            if current.strip():
                tokens.append(current.strip())
            current = ""
        elif ch == "-" and current.strip() and current.strip()[-1] not in "eE":
            if current.strip():
                tokens.append(current.strip())
            current = ch
        else:
            current += ch
    if current.strip():
        tokens.append(current.strip())

    idx = 0
    while idx < len(tokens):
        cmd = tokens[idx]
        if cmd == "M":
            path.moveTo(float(tokens[idx + 1]), float(tokens[idx + 2]))
            idx += 3
        elif cmd == "L":
            path.lineTo(float(tokens[idx + 1]), float(tokens[idx + 2]))
            idx += 3
        elif cmd == "C":
            path.cubicTo(
                float(tokens[idx + 1]),
                float(tokens[idx + 2]),
                float(tokens[idx + 3]),
                float(tokens[idx + 4]),
                float(tokens[idx + 5]),
                float(tokens[idx + 6]),
            )
            idx += 7
        elif cmd == "Z":
            path.closeSubpath()
            idx += 1
        else:
            path.lineTo(float(tokens[idx]), float(tokens[idx + 1]))
            idx += 2
    return path


class _CollapseArrowWidget(QWidget):
    """Internal chevron-right arrow widget using QPainter.

    Draws the NaiveUI ChevronRight SVG path scaled to icon_size.
    Supports rotation for expanded/collapsed state.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("collapse_arrow")
        self._expanded = False
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens and tokens.component_sizes.get("medium"):
            self._icon_size = tokens.component_sizes["medium"].get("icon_size", 18)
        else:
            self._icon_size = 18
        self._chevron_path = _parse_svg_path(_CHEVRON_PATH_DATA)

    def sizeHint(self) -> QSize:
        """Return the preferred size based on the icon_size token."""
        return QSize(self._icon_size, self._icon_size)

    def set_expanded(self, expanded: bool) -> None:
        """Set the expanded state and trigger repaint.

        Args:
            expanded: True for 90-degree rotation, False for 0-degree.
        """
        self._expanded = expanded
        self.update()

    def paintEvent(self, event: object) -> None:
        """Draw the chevron-right path, rotated 90 degrees when expanded."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self.palette().color(QPalette.ColorRole.WindowText)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)

        w = self.width()
        h = self.height()
        scale = min(w, h) / _CHEVRON_VIEWBOX  # Uniform scaling

        # Center offset
        offset_x = (w - _CHEVRON_VIEWBOX * scale) / 2.0
        offset_y = (h - _CHEVRON_VIEWBOX * scale) / 2.0

        transform = QTransform()
        if self._expanded:
            cx = w / 2.0
            cy = h / 2.0
            transform.translate(cx, cy)
            transform.rotate(90)
            transform.translate(-cx, -cy)
        transform.translate(offset_x, offset_y)
        transform.scale(scale, scale)

        painter.setTransform(transform)
        painter.drawPath(self._chevron_path)
        painter.end()



class TCollapseItem(BaseWidget):
    """A single collapsible panel with a clickable header and content area.

    Args:
        name: Unique identifier for this item within its parent TCollapse.
        title: Display text shown in the header bar.
        expanded: Whether the content area is initially expanded.
        disabled: Whether clicking the header is disabled.
        parent: Optional parent widget.

    Signals:
        expanded_changed: Emitted when the expanded state changes,
            carries the new boolean state.

    Example:
        >>> item = TCollapseItem(name="section1", title="Section 1")
        >>> item.set_content(QLabel("Hello"))
        >>> item.expanded_changed.connect(lambda v: print(v))
    """

    expanded_changed = Signal(bool)
    _ANIMATION_DURATION = 200

    def __init__(
        self,
        name: str = "",
        title: str = "",
        expanded: bool = False,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        self._item_name = name
        self._title_text = title
        self._expanded = expanded
        self._disabled = disabled
        self._content_widget: QWidget | None = None
        self._animating = False
        self._arrow_placement: str = "left"
        self._trigger_areas: list[str] = list(_DEFAULT_TRIGGER_AREAS)
        self._custom_title_widget: QWidget | None = None
        self._header_extra_widget: QWidget | None = None
        self._custom_arrow_widget: QWidget | None = None
        self._parent_collapse: TCollapse | None = None
        super().__init__(parent)
        self.setProperty("disabled", str(disabled).lower())
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self._header = QWidget(self)
        self._header.setObjectName("collapse_header")
        self._header.setCursor(
            Qt.CursorShape.ForbiddenCursor if disabled else Qt.CursorShape.PointingHandCursor
        )
        self._header_layout = QHBoxLayout(self._header)
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setSpacing(0)
        self._arrow_label = _CollapseArrowWidget(self._header)
        self._update_arrow()
        self._title_label = QLabel(title, self._header)
        self._title_label.setObjectName("collapse_title")
        self._rebuild_header_layout()
        root.addWidget(self._header)
        self._content_wrapper = QWidget(self)
        self._content_wrapper.setObjectName("collapse_content_wrapper")
        self._content_layout = QVBoxLayout(self._content_wrapper)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        root.addWidget(self._content_wrapper)
        if not expanded:
            self._content_wrapper.setMaximumHeight(0)
            self._content_wrapper.setVisible(False)
        self.apply_theme()

    @property
    def item_name(self) -> str:
        """Return the unique name identifier for this item."""
        return self._item_name

    @property
    def title(self) -> str:
        """Return the header title text."""
        return self._title_text

    @title.setter
    def title(self, value: str) -> None:
        """Set the header title text."""
        self._title_text = value
        self._title_label.setText(value)

    @property
    def expanded(self) -> bool:
        """Return whether the content area is currently expanded."""
        return self._expanded

    @property
    def disabled(self) -> bool:
        """Return whether the item header click is disabled."""
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        """Set the disabled state."""
        self._disabled = value
        self.setProperty("disabled", str(value).lower())
        self._header.setCursor(
            Qt.CursorShape.ForbiddenCursor if value else Qt.CursorShape.PointingHandCursor
        )
        self.style().unpolish(self)
        self.style().polish(self)

    def set_content(self, widget: QWidget) -> None:
        """Set the content widget displayed when expanded."""
        if self._content_widget is not None:
            self._content_layout.removeWidget(self._content_widget)
            self._content_widget.setParent(None)  # type: ignore[call-overload]
        self._content_widget = widget
        self._content_layout.addWidget(widget)

    def set_title(self, widget: QWidget) -> None:
        """Set a custom title widget replacing the default text label."""
        if self._custom_title_widget is not None:
            self._header_layout.removeWidget(self._custom_title_widget)
            self._custom_title_widget.setParent(None)  # type: ignore[call-overload]
        self._custom_title_widget = widget
        widget.setObjectName("collapse_title")
        self._title_label.setVisible(False)
        self._rebuild_header_layout()

    def set_header_extra(self, widget: QWidget) -> None:
        """Set an extra widget in the header bar (beside the arrow)."""
        if self._header_extra_widget is not None:
            self._header_layout.removeWidget(self._header_extra_widget)
            self._header_extra_widget.setParent(None)  # type: ignore[call-overload]
        self._header_extra_widget = widget
        self._rebuild_header_layout()

    def set_arrow(self, widget: QWidget) -> None:
        """Set a custom arrow widget replacing the default arrow indicator."""
        if self._custom_arrow_widget is not None:
            self._header_layout.removeWidget(self._custom_arrow_widget)
            self._custom_arrow_widget.setParent(None)  # type: ignore[call-overload]
        self._custom_arrow_widget = widget
        widget.setObjectName("collapse_arrow")
        self._arrow_label.setVisible(False)
        self._rebuild_header_layout()

    def set_expanded(self, expanded: bool, animate: bool = True) -> None:
        """Expand or collapse the content area."""
        if expanded == self._expanded or self._animating:
            return
        self._expanded = expanded
        self._update_arrow()
        if animate:
            self._animate_toggle(expanded)
        else:
            if expanded:
                self._content_wrapper.setVisible(True)
                self._content_wrapper.setMaximumHeight(16777215)
            else:
                self._content_wrapper.setMaximumHeight(0)
                self._content_wrapper.setVisible(False)
        self.expanded_changed.emit(expanded)

    def toggle(self) -> None:
        """Toggle the expanded state if not disabled."""
        if not self._disabled:
            self.set_expanded(not self._expanded)

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this collapse item."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("collapse.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    def mousePressEvent(self, event: object) -> None:
        """Handle mouse press on the header to toggle expansion."""
        from PySide6.QtGui import QMouseEvent

        if isinstance(event, QMouseEvent) and not self._disabled:
            header_rect = self._header.geometry()
            if header_rect.contains(event.pos()):
                click_pos = event.pos() - header_rect.topLeft()
                area = self._hit_test_area(click_pos)
                if self._parent_collapse is not None:
                    self._parent_collapse.item_header_clicked.emit(self._item_name)
                if area in self._trigger_areas:
                    self.toggle()
                return
        super().mousePressEvent(event)  # type: ignore[arg-type]

    def _set_parent_collapse(self, collapse: TCollapse) -> None:
        """Set the parent TCollapse reference for signal forwarding."""
        self._parent_collapse = collapse

    def _set_arrow_placement(self, placement: str) -> None:
        """Update arrow placement and rebuild header layout."""
        if placement not in ("left", "right"):
            placement = "left"
        self._arrow_placement = placement
        self.setProperty("arrowPlacement", placement)
        self.style().unpolish(self)
        self.style().polish(self)
        self._rebuild_header_layout()

    def _set_trigger_areas(self, areas: list[str]) -> None:
        """Update the trigger areas for this item."""
        self._trigger_areas = [a for a in areas if a in ("main", "extra", "arrow")]

    def _hit_test_area(self, pos: object) -> str:
        """Determine which header area a click position falls in."""
        from PySide6.QtCore import QPoint

        if not isinstance(pos, QPoint):
            return "main"
        arrow_widget = self._custom_arrow_widget if self._custom_arrow_widget else self._arrow_label
        if arrow_widget.isVisible() and arrow_widget.geometry().contains(pos):
            return "arrow"
        if (
            self._header_extra_widget is not None
            and self._header_extra_widget.isVisible()
            and self._header_extra_widget.geometry().contains(pos)
        ):
            return "extra"
        return "main"

    def _rebuild_header_layout(self) -> None:
        """Rebuild the header layout based on arrow_placement and custom widgets."""
        while self._header_layout.count():
            item = self._header_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)  # type: ignore[call-overload]
        arrow_widget = self._custom_arrow_widget if self._custom_arrow_widget else self._arrow_label
        title_widget = self._custom_title_widget if self._custom_title_widget else self._title_label
        arrow_widget.setParent(self._header)
        title_widget.setParent(self._header)
        if self._arrow_placement == "right":
            self._header_layout.addWidget(title_widget)
            self._header_layout.addWidget(arrow_widget)
            self._header_layout.addStretch(1)
            if self._header_extra_widget is not None:
                self._header_extra_widget.setParent(self._header)
                self._header_layout.addWidget(self._header_extra_widget)
        else:
            self._header_layout.addWidget(arrow_widget)
            self._header_layout.addWidget(title_widget, 1)
            if self._header_extra_widget is not None:
                self._header_extra_widget.setParent(self._header)
                self._header_layout.addWidget(self._header_extra_widget)
        arrow_widget.setVisible(True)
        title_widget.setVisible(True)

    def _update_arrow(self) -> None:
        """Update the arrow indicator based on expanded state."""
        if self._custom_arrow_widget is not None:
            return
        self._arrow_label.set_expanded(self._expanded)

    def _animate_toggle(self, expanding: bool) -> None:
        """Run the expand/collapse animation with ease-in-out curve (200ms)."""
        self._animating = True

        # Pin the parent collapse's minimum height to prevent layout jitter
        parent_collapse = self._parent_collapse
        if parent_collapse is not None:
            parent_collapse.setMinimumHeight(parent_collapse.height())

        if expanding:
            # Set max height to 0 BEFORE making visible to prevent flash
            self._content_wrapper.setMaximumHeight(0)
            self._content_wrapper.setVisible(True)
            # Temporarily allow full height to measure sizeHint
            self._content_wrapper.setMaximumHeight(16777215)
            target_height = self._content_wrapper.sizeHint().height()
            # Clamp back to 0 before starting animation
            self._content_wrapper.setMaximumHeight(0)
        else:
            target_height = 0
        start_height = self._content_wrapper.maximumHeight() if not expanding else 0
        anim = QPropertyAnimation(self._content_wrapper, b"maximumHeight", self)
        anim.setDuration(self._ANIMATION_DURATION)
        anim.setStartValue(start_height)
        anim.setEndValue(target_height)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        if expanding:
            anim.finished.connect(self._on_expand_finished)
        else:
            anim.finished.connect(self._on_collapse_finished)
        anim.start()

    def _on_expand_finished(self) -> None:
        """Called when expand animation completes."""
        self._animating = False
        self._content_wrapper.setMaximumHeight(16777215)
        if self._parent_collapse is not None:
            self._parent_collapse.setMinimumHeight(0)

    def _on_collapse_finished(self) -> None:
        """Called when collapse animation completes."""
        self._animating = False
        self._content_wrapper.setVisible(False)
        if self._parent_collapse is not None:
            self._parent_collapse.setMinimumHeight(0)


class TCollapse(BaseWidget):
    """Accordion-style collapsible panel container.

    Manages a set of TCollapseItem children. Supports accordion mode
    (only one item expanded at a time), initial expanded state control,
    arrow placement configuration, and trigger area control.

    Args:
        accordion: If True, only one item can be expanded at a time.
        expanded_names: List of item names to expand initially.
        arrow_placement: Position of the arrow indicator ("left" or "right").
        trigger_areas: List of areas that trigger expand/collapse on click.
            Valid values: "main", "extra", "arrow". Defaults to all three.
        parent: Optional parent widget.

    Signals:
        item_expanded: Emitted when any item's expanded state changes,
            carries (item_name, is_expanded).
        item_header_clicked: Emitted when any item's header bar is clicked,
            carries the item name.

    Example:
        >>> collapse = TCollapse(accordion=True, arrow_placement="right")
        >>> item1 = TCollapseItem(name="a", title="Section A")
        >>> item1.set_content(QLabel("Content A"))
        >>> collapse.add_item(item1)
    """

    item_expanded = Signal(str, bool)
    item_header_clicked = Signal(str)

    def __init__(
        self,
        accordion: bool = False,
        expanded_names: list[str] | None = None,
        arrow_placement: str = "left",
        trigger_areas: list[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        self._accordion = accordion
        self._expanded_names = expanded_names or []
        self._arrow_placement = arrow_placement if arrow_placement in ("left", "right") else "left"
        self._trigger_areas = (
            [a for a in trigger_areas if a in ("main", "extra", "arrow")]
            if trigger_areas is not None
            else list(_DEFAULT_TRIGGER_AREAS)
        )
        self._items: list[TCollapseItem] = []
        super().__init__(parent)
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)
        self.apply_theme()

    @property
    def accordion(self) -> bool:
        """Return whether accordion mode is enabled."""
        return self._accordion

    @accordion.setter
    def accordion(self, value: bool) -> None:
        """Set accordion mode."""
        self._accordion = value

    @property
    def arrow_placement(self) -> str:
        """Return the arrow placement setting ("left" or "right")."""
        return self._arrow_placement

    @arrow_placement.setter
    def arrow_placement(self, value: str) -> None:
        """Set arrow placement and update all items."""
        if value not in ("left", "right"):
            value = "left"
        self._arrow_placement = value
        for item in self._items:
            item._set_arrow_placement(value)

    @property
    def trigger_areas(self) -> list[str]:
        """Return the list of trigger areas."""
        return list(self._trigger_areas)

    @trigger_areas.setter
    def trigger_areas(self, value: list[str]) -> None:
        """Set trigger areas and update all items."""
        self._trigger_areas = [a for a in value if a in ("main", "extra", "arrow")]
        for item in self._items:
            item._set_trigger_areas(self._trigger_areas)

    @property
    def items(self) -> list[TCollapseItem]:
        """Return the list of managed collapse items."""
        return list(self._items)

    def add_item(self, item: TCollapseItem) -> None:
        """Add a collapse item to this container.

        If the item's name is in expanded_names, it will be expanded.
        Connects the item's expanded_changed signal for accordion logic.
        Applies current arrow_placement and trigger_areas settings.
        Sets the firstItem property based on position for divider styling.

        Args:
            item: The TCollapseItem to add.
        """
        is_first = len(self._items) == 0
        self._items.append(item)
        item.setParent(self)
        item._set_parent_collapse(self)
        item._set_arrow_placement(self._arrow_placement)
        item._set_trigger_areas(self._trigger_areas)
        item.setProperty("firstItem", "true" if is_first else "false")
        self._root_layout.addWidget(item)
        item.style().unpolish(item)
        item.style().polish(item)
        item.expanded_changed.connect(lambda exp, i=item: self._on_item_expanded(i, exp))
        if item.item_name in self._expanded_names:
            item.set_expanded(True, animate=False)


    def remove_item(self, item: TCollapseItem) -> None:
        """Remove a collapse item from this container."""
        if item in self._items:
            self._items.remove(item)
            self._root_layout.removeWidget(item)
            item._parent_collapse = None
            item.setParent(None)  # type: ignore[call-overload]
            # Re-assign firstItem property for remaining items
            for idx, remaining in enumerate(self._items):
                remaining.setProperty("firstItem", "true" if idx == 0 else "false")
                remaining.style().unpolish(remaining)
                remaining.style().polish(remaining)

    def get_expanded_names(self) -> list[str]:
        """Return the names of all currently expanded items."""
        return [item.item_name for item in self._items if item.expanded]

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this collapse container."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("collapse.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    def _on_item_expanded(self, item: TCollapseItem, expanded: bool) -> None:
        """Handle an item's expanded state change.

        In accordion mode, collapses all other items when one expands.
        """
        if expanded and self._accordion:
            for other in self._items:
                if other is not item and other.expanded:
                    other.set_expanded(False)
        self.item_expanded.emit(item.item_name, expanded)
