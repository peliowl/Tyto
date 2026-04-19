"""TMenu organism component: navigation menu with vertical/horizontal modes.

Provides TMenuItem, TMenuItemGroup, and TMenu for building multi-level
navigation structures with route awareness, collapse animation, and
active item highlighting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSize,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QIcon, QMouseEvent, QPainter, QPainterPath, QPalette, QPen, QTransform
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color

# NaiveUI ChevronRight SVG path (viewBox 0 0 16 16) — shared with collapse
_CHEVRON_PATH_DATA = (
    "M5.64645 3.14645C5.45118 3.34171 5.45118 3.65829 5.64645 3.85355"
    "L9.79289 8L5.64645 12.1464C5.45118 12.3417 5.45118 12.6583 5.64645 12.8536"
    "C5.84171 13.0488 6.15829 13.0488 6.35355 12.8536L10.8536 8.35355"
    "C11.0488 8.15829 11.0488 7.84171 10.8536 7.64645L6.35355 3.14645"
    "C6.15829 2.95118 5.84171 2.95118 5.64645 3.14645Z"
)
_CHEVRON_VIEWBOX = 16.0


@dataclass
class MenuOption:
    """Menu item metadata carried by the item_selected signal.

    Attributes:
        key: Unique identifier for the menu item.
        label: Display text for the menu item.
        icon: Optional icon associated with the menu item.
    """

    key: str = ""
    label: str = ""
    icon: QIcon | None = field(default=None, repr=False)


class _MenuPopupContainer(QWidget):
    """Inner container that paints rounded-rect background and border.

    Required because the parent popup uses WA_TranslucentBackground,
    which prevents QSS background-color from rendering.  The container
    reads Design Tokens from ThemeEngine at paint time so it always
    reflects the active theme.
    """

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint rounded-rect background and 1px border using theme tokens."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            engine = ThemeEngine.instance()
            bg = parse_color(str(engine.get_token("colors", "popover_color")))
            border_c = parse_color(str(engine.get_token("colors", "divider")))
            radius = int(engine.get_token("radius", "large"))
        except Exception:
            bg = QColor("#ffffff")
            border_c = QColor("#efeff5")
            radius = 8

        pen = QPen(border_c)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(bg)
        rect = QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()


def _parse_svg_path(data: str) -> QPainterPath:
    """Parse a simplified SVG path string into a QPainterPath."""
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
                float(tokens[idx + 1]), float(tokens[idx + 2]),
                float(tokens[idx + 3]), float(tokens[idx + 4]),
                float(tokens[idx + 5]), float(tokens[idx + 6]),
            )
            idx += 7
        elif cmd == "Z":
            path.closeSubpath()
            idx += 1
        else:
            path.lineTo(float(tokens[idx]), float(tokens[idx + 1]))
            idx += 2
    return path


class _MenuArrowWidget(QWidget):
    """Chevron arrow widget for menu group expand/collapse indicator.

    Draws the NaiveUI ChevronRight SVG path, rotated 90 degrees when expanded.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("menu_group_arrow")
        self._expanded = False
        self._icon_size = 16
        self._icon_color = "#333639"
        self._chevron_path = _parse_svg_path(_CHEVRON_PATH_DATA)

    def apply_theme(self) -> None:
        """Read arrow color from ThemeEngine tokens."""
        engine = ThemeEngine.instance()
        if engine.current_theme():
            try:
                self._icon_color = str(engine.get_token("colors", "text_primary"))
            except Exception:
                pass
            self.update()

    def sizeHint(self) -> QSize:
        """Return the preferred size."""
        return QSize(self._icon_size, self._icon_size)

    def set_expanded(self, expanded: bool) -> None:
        """Set the expanded state and trigger repaint."""
        self._expanded = expanded
        self.update()

    def paintEvent(self, event: object) -> None:
        """Draw the chevron-right path, rotated 90 degrees when expanded."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = parse_color(self._icon_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        w = self.width()
        h = self.height()
        scale = min(w, h) / _CHEVRON_VIEWBOX
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


class _CollapseToggleButton(QWidget):
    """Circular toggle button for menu collapse/expand.

    Positioned at the right edge of TMenu, half-protruding beyond
    the menu boundary. Draws a chevron icon pointing left (collapse)
    or right (expand) based on the current state.
    """

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._collapsed = False
        self._disabled = False
        self._menu_ref: QWidget | None = None

        # Token-derived visual properties (defaults until apply_theme is called)
        self._bg_color = "#ffffff"
        self._border_color = "#e0e0e6"
        self._icon_color = "#666666"
        self._disabled_icon_color = "#c2c2c8"
        self._btn_size = 28

        self._chevron_path = _parse_svg_path(_CHEVRON_PATH_DATA)
        self._rotation = 180.0  # expanded = 180° (points left)
        self._rotation_anim: QPropertyAnimation | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setFixedSize(self._btn_size, self._btn_size)

    def apply_theme(self) -> None:
        """Read colors and size from ThemeEngine tokens."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            self._bg_color = str(engine.get_token("colors", "collapse_toggle_bg"))
            self._border_color = str(engine.get_token("colors", "collapse_toggle_border"))
            self._icon_color = str(engine.get_token("colors", "text_primary"))
            self._disabled_icon_color = str(engine.get_token("colors", "text_disabled"))
            tokens = engine.current_tokens()
            if tokens and tokens.component_sizes.get("small"):
                self._btn_size = tokens.component_sizes["small"].get("height", 28)
            self.setFixedSize(self._btn_size, self._btn_size)
            self.update()
        except Exception:
            pass

    def sizeHint(self) -> QSize:
        """Return the preferred size based on token-derived button size."""
        return QSize(self._btn_size, self._btn_size)

    def set_collapsed(self, collapsed: bool) -> None:
        """Update the collapsed state with rotation animation.

        Args:
            collapsed: Whether the parent menu is collapsed.
        """
        self._collapsed = collapsed
        # Animate chevron rotation: 0° = right (>), 180° = left (<)
        target = 0.0 if collapsed else 180.0
        if self._rotation_anim is not None:
            self._rotation_anim.stop()
        self._rotation_anim = QPropertyAnimation(self, b"rotation", self)
        self._rotation_anim.setDuration(200)
        self._rotation_anim.setStartValue(self._rotation)
        self._rotation_anim.setEndValue(target)
        self._rotation_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._rotation_anim.start()

    def set_disabled(self, disabled: bool) -> None:
        """Update the disabled state, change cursor, and repaint.

        Args:
            disabled: Whether interaction should be blocked.
        """
        self._disabled = disabled
        self.setCursor(
            Qt.CursorShape.ForbiddenCursor if disabled else Qt.CursorShape.PointingHandCursor
        )
        self.update()

    def reposition(self) -> None:
        """Position the button at the menu's right edge, half-protruding.

        If the menu has a parent widget, the button is reparented to that
        parent so it is not clipped by the menu's bounds.
        """
        menu = self._menu_ref
        if menu is None:
            return

        menu_parent = menu.parentWidget()
        if menu_parent is not None and self.parentWidget() is not menu_parent:
            self.setParent(menu_parent)
            self.show()

        half = self._btn_size // 2

        if self.parentWidget() is menu_parent and menu_parent is not None:
            menu_pos = menu.pos()
            x = menu_pos.x() + menu.width() - half
            y = menu_pos.y() + (menu.height() - self._btn_size) // 2
        else:
            x = menu.width() - half
            y = (menu.height() - self._btn_size) // 2

        self.move(x, y)
        self.raise_()

    def paintEvent(self, event: object) -> None:
        """Draw circular background, border, and chevron icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Inset by 1 full pixel so the anti-aliased stroke never touches
        # the widget boundary (prevents top/left 1px clipping artifacts).
        pen_width = 1.0
        inset = 1.0

        # Draw circular background (no hover effect)
        bg = parse_color(self._bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawEllipse(inset, inset, w - inset * 2, h - inset * 2)

        # Draw circular border (skip if transparent, e.g. dark mode)
        if self._border_color and self._border_color.lower() != "transparent":
            border_color = parse_color(self._border_color)
            painter.setPen(QPen(border_color, pen_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(inset, inset, w - inset * 2, h - inset * 2)

        # Draw chevron icon
        icon_color = parse_color(self._disabled_icon_color if self._disabled else self._icon_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(icon_color)

        icon_size = min(w, h) * 0.55
        scale = icon_size / _CHEVRON_VIEWBOX
        offset_x = (w - _CHEVRON_VIEWBOX * scale) / 2.0
        offset_y = (h - _CHEVRON_VIEWBOX * scale) / 2.0

        transform = QTransform()
        # Use animated rotation value (180° = left, 0° = right)
        if self._rotation != 0.0:
            cx = w / 2.0
            cy = h / 2.0
            transform.translate(cx, cy)
            transform.rotate(self._rotation)
            transform.translate(-cx, -cy)
        transform.translate(offset_x, offset_y)
        transform.scale(scale, scale)

        painter.setTransform(transform)
        painter.drawPath(self._chevron_path)
        painter.end()

    def enterEvent(self, event: object) -> None:  # type: ignore[override]
        """No hover effect for collapse toggle button."""
        super().enterEvent(event)  # type: ignore[arg-type]


    def leaveEvent(self, event: object) -> None:  # type: ignore[override]
        """No hover effect for collapse toggle button."""
        super().leaveEvent(event)  # type: ignore[arg-type]


    def mousePressEvent(self, event: object) -> None:
        """Emit clicked signal if not disabled."""
        if not self._disabled:
            self.clicked.emit()
        # Accept the event to prevent propagation to parent widgets
        if isinstance(event, QMouseEvent):
            event.accept()

    def _get_rotation(self) -> float:
        return self._rotation

    def _set_rotation(self, value: float) -> None:
        self._rotation = value
        self.update()

    rotation = Property(float, _get_rotation, _set_rotation)


class TMenuItem(BaseWidget):
    """Single menu item with key, label, and optional icon.

    Args:
        key: Unique identifier for this menu item.
        label: Display text for the item.
        icon: Optional icon displayed before the label.
        disabled: Whether the item is disabled.
        parent: Optional parent widget.

    Signals:
        clicked: Emitted with the item key when clicked.

    Example:
        >>> item = TMenuItem(key="home", label="Home")
        >>> item.clicked.connect(lambda k: print(f"Selected: {k}"))
    """

    clicked = Signal(str)

    def __init__(
        self,
        key: str,
        label: str = "",
        icon: QIcon | None = None,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        self._key = key
        self._label_text = label
        self._icon = icon
        self._disabled = disabled
        self._menu_disabled = False
        self._active = False
        self._indent_level = 0

        super().__init__(parent)

        self.setProperty("active", "false")
        self.setProperty("itemDisabled", str(disabled).lower())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(
            Qt.CursorShape.ForbiddenCursor if disabled else Qt.CursorShape.PointingHandCursor
        )

        self._build_ui()
        self.apply_theme()

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the item row with optional icon and label."""
        root = QVBoxLayout(self)
        # Horizontal inset for the rounded-rect hover background effect.
        # Applied on the outer layout so Qt sizeHint includes it.
        engine = ThemeEngine.instance()
        h_margin = 8  # fallback = spacing.medium
        h_pad = 20  # fallback = menu.item_padding_h
        item_h = 40  # fallback = menu.item_height
        if engine.current_theme():
            tokens = engine.current_tokens()
            if tokens:
                if tokens.spacing:
                    h_margin = tokens.spacing.get("medium", 8)
                if tokens.menu:
                    h_pad = tokens.menu.get("item_padding_h", 20)
                    item_h = tokens.menu.get("item_height", 40)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._row = QWidget(self)
        self._row.setObjectName("menu_item_row")
        self._row.setFixedHeight(item_h)
        self._row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row_layout = QHBoxLayout(self._row)
        row_layout.setContentsMargins(h_pad, 0, h_pad, 0)
        row_layout.setSpacing(8)

        # Icon label (text-based icon placeholder or QIcon)
        self._icon_label = QLabel(self._row)
        self._icon_label.setObjectName("menu_item_icon")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setFixedWidth(24)
        if self._icon is not None:
            self._icon_label.setPixmap(self._icon.pixmap(16, 16))
        else:
            self._icon_label.setVisible(False)
        row_layout.addWidget(self._icon_label)

        # Text label
        self._text_label = QLabel(self._label_text, self._row)
        self._text_label.setObjectName("menu_item_label")
        row_layout.addWidget(self._text_label)
        row_layout.addStretch()

        root.addWidget(self._row)

    # -- Public API -----------------------------------------------------------

    @property
    def key(self) -> str:
        """Return the unique key identifier."""
        return self._key

    @property
    def label(self) -> str:
        """Return the display label text."""
        return self._label_text

    @property
    def disabled(self) -> bool:
        """Return whether the item is disabled."""
        return self._disabled

    def set_active(self, active: bool) -> None:
        """Set the active (highlighted) state.

        Args:
            active: Whether this item should be highlighted.
        """
        self._active = active
        self.setProperty("active", str(active).lower())
        self._apply_active_colors()

    def _apply_active_colors(self) -> None:
        """Apply text/icon colors based on active and disabled state."""
        if not hasattr(self, "_text_label"):
            return
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        effectively_disabled = self._disabled or self._menu_disabled
        if effectively_disabled:
            color = engine.get_token("colors", "text_disabled")
            icon_color = color
        elif self._active:
            color = engine.get_token("colors", "primary")
            icon_color = color
        else:
            color = engine.get_token("colors", "text_primary")
            icon_color = engine.get_token("colors", "text_title")
        font_size = engine.get_token("font_sizes", "medium")
        self._text_label.setStyleSheet(
            f"color: {color}; font-size: {font_size}px; background: transparent; border: none;"
        )
        self._icon_label.setStyleSheet(
            f"color: {icon_color}; background: transparent; border: none;"
        )
        # Row: clear any inline stylesheet so QSS :hover from TMenu works
        self._row.setStyleSheet("")

    def is_active(self) -> bool:
        """Return whether this item is currently active."""
        return self._active

    def set_icon(self, icon: QIcon | None) -> None:
        """Set or clear the item icon at runtime.

        Args:
            icon: QIcon to display, or None to hide the icon area.
        """
        self._icon = icon
        if icon is not None:
            self._icon_label.setPixmap(icon.pixmap(16, 16))
            self._icon_label.setVisible(True)
        else:
            self._icon_label.setVisible(False)
        # Notify parent layout that our size requirements changed
        self._row.updateGeometry()
        self.updateGeometry()
        self.adjustSize()

    def set_indent_level(self, level: int) -> None:
        """Set the indentation level for nested items.

        Each level adds ``menu.indent`` px to the base ``menu.item_padding_h``
        left margin, preserving the base horizontal padding.

        Args:
            level: Nesting depth (0 = top level).
        """
        self._indent_level = level
        engine = ThemeEngine.instance()
        indent = 24  # fallback
        base_pad = 20  # fallback = menu.item_padding_h
        if engine.current_theme():
            tokens = engine.current_tokens()
            if tokens and tokens.menu:
                indent = tokens.menu.get("indent", 24)
                base_pad = tokens.menu.get("item_padding_h", 20)
        left_margin = base_pad + indent * level
        layout = self._row.layout()
        if layout is not None:
            m = layout.contentsMargins()
            # Always restore right margin from token; collapsed mode sets it
            # to 0 and the stale value would otherwise persist.
            layout.setContentsMargins(left_margin, m.top(), base_pad, m.bottom())

    def set_collapsed_mode(self, collapsed: bool) -> None:
        """Toggle collapsed display (icon only, hide label).

        Args:
            collapsed: Whether to show only the icon.
        """
        self._text_label.setVisible(not collapsed)
        row_layout = self._row.layout()
        if row_layout is not None:
            if collapsed:
                # Remove margins so icon can center in the full row width
                m = row_layout.contentsMargins()
                row_layout.setContentsMargins(0, m.top(), 0, m.bottom())
                # Remove the trailing stretch so icon can truly center
                last_idx = row_layout.count() - 1
                if last_idx >= 0:
                    spacer = row_layout.itemAt(last_idx)
                    if spacer is not None and spacer.widget() is None:
                        row_layout.removeItem(spacer)
                # Let icon label expand to fill the row, centering its pixmap
                self._icon_label.setFixedWidth(16777215)  # QWIDGETSIZE_MAX
                self._icon_label.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
                )
            else:
                # Restore fixed icon width and indent
                self._icon_label.setFixedWidth(24)
                self._icon_label.setSizePolicy(
                    QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
                )
                # Re-add stretch if missing
                has_stretch = False
                for i in range(row_layout.count()):
                    item = row_layout.itemAt(i)
                    if item is not None and item.widget() is None:
                        has_stretch = True
                        break
                if not has_stretch:
                    row_layout.addStretch()
                row_layout.setAlignment(Qt.AlignmentFlag(0))
                self.set_indent_level(self._indent_level)

    def set_horizontal_layout(self, horizontal: bool) -> None:
        """Adjust layout for horizontal vs vertical mode.

        Args:
            horizontal: True for horizontal mode, False for vertical.
        """
        self._is_horizontal = horizontal
        # Re-apply colors since mode affects row background
        self._apply_active_colors()

    # -- Theme ----------------------------------------------------------------

    def apply_theme(self) -> None:
        """Apply the current theme to this menu item.

        Note: stylesheet is set by the parent TMenu for base styling.
        Active/inactive colors are applied directly via _apply_active_colors.
        """
        if not hasattr(self, "_row"):
            return
        self._apply_active_colors()

    # -- Events ---------------------------------------------------------------

    def set_menu_disabled(self, disabled: bool) -> None:
        """Set the menu-level disabled state (propagated from TMenu).

        This is separate from the item's own disabled state.
        The item is effectively disabled if either flag is True.

        Args:
            disabled: Whether the parent menu is disabled.
        """
        self._menu_disabled = disabled
        effectively_disabled = self._disabled or self._menu_disabled
        self.setProperty("itemDisabled", str(effectively_disabled).lower())
        self.setCursor(
            Qt.CursorShape.ForbiddenCursor if effectively_disabled
            else Qt.CursorShape.PointingHandCursor
        )
        self._apply_active_colors()

    def mousePressEvent(self, event: object) -> None:
        """Emit clicked signal on mouse press if not disabled."""
        if isinstance(event, QMouseEvent) and not self._disabled and not self._menu_disabled:
            self.clicked.emit(self._key)
            self._emit_bus_event("clicked", self._key)

    def enterEvent(self, event: object) -> None:  # type: ignore[override]
        """Show hover background on mouse enter."""
        super().enterEvent(event)  # type: ignore[arg-type]
        if self._disabled or self._menu_disabled:
            return
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        hover_color = engine.get_token("colors", "hover_color")
        radius = engine.get_token("radius", "medium")
        is_horiz = getattr(self, "_is_horizontal", False)
        if is_horiz:
            self.setStyleSheet(
                f"background-color: {hover_color}; border: none; border-radius: 0px;"
            )
        else:
            self.setStyleSheet(
                f"background-color: {hover_color}; border: none; border-radius: {radius}px;"
            )
        self._emit_bus_event("mouse_enter", event)

    def leaveEvent(self, event: object) -> None:  # type: ignore[override]
        """Remove hover background on mouse leave."""
        super().leaveEvent(event)  # type: ignore[arg-type]
        self.setStyleSheet("")
        self._emit_bus_event("mouse_leave", event)


class TMenuItemGroup(BaseWidget):
    """Submenu group supporting multi-level nesting with expand/collapse animation.

    Each nesting level indents children by 24px (menu.indent token).
    Clicking the header toggles the child list visibility with a 200ms
    ease-in-out animation on ``maximumHeight``.

    Args:
        key: Unique identifier for this group.
        label: Display text for the group header.
        icon: Optional icon displayed before the label.
        expanded: Whether the group is initially expanded.
        parent: Optional parent widget.

    Signals:
        expanded_changed: Emitted with the new expanded state on toggle.

    Example:
        >>> group = TMenuItemGroup(key="settings", label="Settings")
        >>> group.add_item(TMenuItem(key="profile", label="Profile"))
    """

    expanded_changed = Signal(bool)

    _ANIMATION_DURATION = 200

    def __init__(
        self,
        key: str,
        label: str = "",
        icon: QIcon | None = None,
        expanded: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        self._key = key
        self._label_text = label
        self._icon = icon
        self._expanded = expanded
        self._items: list[TMenuItem | TMenuItemGroup] = []
        self._animating = False
        self._indent_level = 0
        self._menu_disabled = False
        self._menu_mode: Any = None
        self._collapsed_mode = False
        self._popup: QWidget | None = None
        self._hide_timer: QTimer | None = None
        self._owner_group: TMenuItemGroup | None = None

        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._build_ui()
        self.apply_theme()

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the group header and collapsible children container."""
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header row
        self._header = QWidget(self)
        self._header.setObjectName("menu_group_header")
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        header_layout = QHBoxLayout(self._header)
        # Use code-level margins instead of QSS padding for proper sizeHint.
        engine = ThemeEngine.instance()
        h_pad = 20  # fallback = menu.item_padding_h
        if engine.current_theme():
            tokens = engine.current_tokens()
            if tokens and tokens.menu:
                h_pad = tokens.menu.get("item_padding_h", 20)
        # Right margin is intentionally small (2px) so the expand/collapse
        # arrow sits close to the right edge, matching NaiveUI style.
        header_layout.setContentsMargins(h_pad, 0, 4, 0)
        header_layout.setSpacing(8)

        # Icon
        self._icon_label = QLabel(self._header)
        self._icon_label.setObjectName("menu_group_icon")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setFixedWidth(24)
        if self._icon is not None:
            self._icon_label.setPixmap(self._icon.pixmap(16, 16))
        else:
            self._icon_label.setVisible(False)
        header_layout.addWidget(self._icon_label)

        # Label
        self._text_label = QLabel(self._label_text, self._header)
        self._text_label.setObjectName("menu_group_label")
        header_layout.addWidget(self._text_label, 1)

        # Arrow indicator (chevron widget matching NaiveUI style)
        self._arrow_label = _MenuArrowWidget(self._header)
        self._arrow_label.setFixedSize(16, 16)
        self._update_arrow()
        header_layout.addWidget(self._arrow_label)

        root.addWidget(self._header)

        # Children container (animated via maximumHeight)
        self._children_wrapper = QWidget(self)
        self._children_wrapper.setObjectName("menu_group_children")
        self._children_wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._children_layout = QVBoxLayout(self._children_wrapper)
        self._children_layout.setContentsMargins(0, 0, 0, 0)
        self._children_layout.setSpacing(0)
        root.addWidget(self._children_wrapper)

        # Set initial state without animation
        if not self._expanded:
            self._children_wrapper.setMaximumHeight(0)
            self._children_wrapper.setVisible(False)

    # -- Public API -----------------------------------------------------------

    @property
    def key(self) -> str:
        """Return the unique key identifier."""
        return self._key

    @property
    def label(self) -> str:
        """Return the group header label text."""
        return self._label_text

    def is_expanded(self) -> bool:
        """Return whether the group is currently expanded."""
        return self._expanded

    def set_expanded(self, expanded: bool, animate: bool = True) -> None:
        """Expand or collapse the children container.

        Args:
            expanded: True to expand, False to collapse.
            animate: Whether to use animation (default True).
        """
        if expanded == self._expanded or self._animating:
            return

        self._expanded = expanded
        self._update_arrow()

        if animate:
            self._animate_toggle(expanded)
        else:
            if expanded:
                self._children_wrapper.setVisible(True)
                self._children_wrapper.setMaximumHeight(16777215)
            else:
                self._children_wrapper.setMaximumHeight(0)
                self._children_wrapper.setVisible(False)

        self.expanded_changed.emit(expanded)
        self._emit_bus_event("expanded_changed", expanded)

    def add_item(self, item: TMenuItem | TMenuItemGroup) -> None:
        """Add a child menu item or sub-group.

        Args:
            item: TMenuItem or TMenuItemGroup to add as a child.
        """
        self._items.append(item)
        item.setParent(self._children_wrapper)
        self._children_layout.addWidget(item)

        # Apply indentation to child items
        child_level = self._indent_level + 1
        item.set_indent_level(child_level)

    def get_items(self) -> list[TMenuItem | TMenuItemGroup]:
        """Return the list of direct child items."""
        return list(self._items)

    def set_icon(self, icon: QIcon | None) -> None:
        """Set or clear the group header icon at runtime.

        Args:
            icon: QIcon to display, or None to hide the icon area.
        """
        self._icon = icon
        if icon is not None:
            self._icon_label.setPixmap(icon.pixmap(16, 16))
            self._icon_label.setVisible(True)
        else:
            self._icon_label.setVisible(False)

    def set_indent_level(self, level: int) -> None:
        """Set the indentation level for this group header.

        Each level adds ``menu.indent`` px to the base ``menu.item_padding_h``
        left margin, preserving the base horizontal padding.

        Args:
            level: Nesting depth (0 = top level).
        """
        self._indent_level = level
        engine = ThemeEngine.instance()
        indent = 24
        base_pad = 20  # fallback = menu.item_padding_h
        if engine.current_theme():
            tokens = engine.current_tokens()
            if tokens and tokens.menu:
                indent = tokens.menu.get("indent", 24)
                base_pad = tokens.menu.get("item_padding_h", 20)
        left_margin = base_pad + indent * level
        layout = self._header.layout()
        if layout is not None:
            m = layout.contentsMargins()
            # Right margin is intentionally small (2px) so the arrow sits
            # close to the right edge; collapsed mode sets it to 0 and the
            # stale value would otherwise persist.
            layout.setContentsMargins(left_margin, m.top(), 4, m.bottom())
        self._apply_indent_to_children()

    def set_collapsed_mode(self, collapsed: bool) -> None:
        """Toggle collapsed display (icon only, hide label and children).

        In collapsed mode, children are shown in a popup on hover (like
        horizontal mode) instead of inline.

        Args:
            collapsed: Whether to show only the icon.
        """
        self._collapsed_mode = collapsed
        self._text_label.setVisible(not collapsed)
        self._arrow_label.setVisible(not collapsed)
        if self._icon is not None:
            self._icon_label.setVisible(True)

        if collapsed:
            # Hide inline children; popup will show on hover
            self._children_wrapper.setVisible(False)
            # Center the icon: remove margins, expand icon label
            header_layout = self._header.layout()
            if header_layout is not None:
                m = header_layout.contentsMargins()
                header_layout.setContentsMargins(0, m.top(), 0, m.bottom())
            self._icon_label.setFixedWidth(16777215)  # QWIDGETSIZE_MAX
            self._icon_label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
        else:
            # Restore icon width, alignment, and indent
            self._icon_label.setFixedWidth(24)
            self._icon_label.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
            )
            header_layout = self._header.layout()
            if header_layout is not None:
                header_layout.setAlignment(Qt.AlignmentFlag(0))
            self.set_indent_level(self._indent_level)
            # Restore inline children and destroy popup if it exists
            if self._popup is not None:
                for item in self._items:
                    item.setParent(self._children_wrapper)
                    self._children_layout.addWidget(item)
                    # Restore nested groups to inline expand/collapse mode
                    # after being in popup mode (_create_popup hid their
                    # _children_wrapper and forced arrow to right-pointing).
                    if isinstance(item, TMenuItemGroup):
                        # Destroy the nested group's own popup first so its
                        # children are reparented back to its _children_wrapper.
                        if item._popup is not None:
                            for child in item._items:
                                child.setParent(item._children_wrapper)
                                item._children_layout.addWidget(child)
                            item._popup.hide()
                            item._popup.deleteLater()
                            item._popup = None
                        item._arrow_label.setVisible(True)
                        item._update_arrow()
                        if item._expanded:
                            item._children_wrapper.setVisible(True)
                        item._apply_indent_to_children()
                        item._owner_group = None
                self._popup.hide()
                self._popup.deleteLater()
                self._popup = None
            if self._expanded:
                self._children_wrapper.setVisible(True)

    def set_menu_mode(self, mode: Any) -> None:
        """Set the display mode for this group.

        In HORIZONTAL mode, children are shown in a popup widget on hover
        instead of inline. The popup is positioned below the group header
        for top-level groups, or to the right for nested groups.

        Args:
            mode: The MenuMode value to apply.
        """
        self._menu_mode = mode

        # Propagate to child groups
        for item in self._items:
            if isinstance(item, TMenuItemGroup):
                item.set_menu_mode(mode)

        # In horizontal mode, hide the inline children wrapper and arrow
        if self._menu_mode is not None and self._menu_mode.value == "horizontal":
            self._children_wrapper.setVisible(False)
            self._arrow_label.setVisible(False)
        else:
            # Restore vertical mode defaults
            if self._popup is not None:
                # Reparent child items back to the inline children wrapper
                # BEFORE destroying the popup, otherwise PySide6 will delete
                # the C++ objects of the children along with the popup.
                for item in self._items:
                    item.setParent(self._children_wrapper)
                    self._children_layout.addWidget(item)
                    # Restore nested groups to inline expand/collapse mode
                    # after being in popup mode (_create_popup hid their
                    # _children_wrapper and forced arrow to right-pointing).
                    if isinstance(item, TMenuItemGroup):
                        # Destroy the nested group's own popup first so its
                        # children are reparented back to its _children_wrapper.
                        if item._popup is not None:
                            for child in item._items:
                                child.setParent(item._children_wrapper)
                                item._children_layout.addWidget(child)
                            item._popup.hide()
                            item._popup.deleteLater()
                            item._popup = None
                        item._arrow_label.setVisible(True)
                        item._update_arrow()
                        if item._expanded:
                            item._children_wrapper.setVisible(True)
                        item._apply_indent_to_children()
                        item._owner_group = None
                self._popup.hide()
                self._popup.deleteLater()
                self._popup = None
            self._arrow_label.setVisible(True)
            if self._expanded:
                self._children_wrapper.setVisible(True)
            # Restore child indent levels after reparenting from popup
            self._apply_indent_to_children()

    def _is_horizontal_mode(self) -> bool:
        """Check if the current mode is horizontal."""
        return self._menu_mode is not None and self._menu_mode.value == "horizontal"

    def _is_nested_group(self) -> bool:
        """Check if this group is nested inside another TMenuItemGroup.

        Also returns True when this group lives inside a popup container
        (``_MenuPopupContainer``), because that means a parent
        ``TMenuItemGroup`` reparented us into its popup — we are still
        logically nested even though the Qt parent chain no longer
        contains a ``TMenuItemGroup``.
        """
        p = self.parent()
        while p is not None:
            if isinstance(p, TMenuItemGroup):
                return True
            if isinstance(p, _MenuPopupContainer):
                return True
            p = p.parent()  # type: ignore[assignment]
        return False

    def _create_popup(self) -> QWidget:
        """Create the popup widget for horizontal/collapsed mode.

        Uses WA_TranslucentBackground + _MenuPopupContainer self-painting
        + QGraphicsDropShadowEffect to achieve NaiveUI-style popover visuals.

        Returns:
            The popup QWidget containing child items.
        """
        popup = QWidget(
            None,
            Qt.WindowType.Tool  # type: ignore[arg-type]
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        popup.setObjectName("menu_popup")

        # Root layout with margins for shadow rendering space
        shadow_margin = 8
        root_layout = QVBoxLayout(popup)
        root_layout.setContentsMargins(
            shadow_margin, shadow_margin, shadow_margin, shadow_margin
        )
        root_layout.setSpacing(0)

        # Inner container with self-painted background
        container = _MenuPopupContainer(popup)
        container.setObjectName("menu_popup_container")

        # Apply shadow effect on container
        shadow = QGraphicsDropShadowEffect(container)
        self._apply_shadow_from_token(shadow)
        container.setGraphicsEffect(shadow)

        # Container layout with vertical padding from spacing.small
        try:
            engine = ThemeEngine.instance()
            v_pad = int(engine.get_token("spacing", "small"))
        except Exception:
            v_pad = 4
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, v_pad, 0, v_pad)
        container_layout.setSpacing(0)

        for item in self._items:
            item.setParent(container)
            container_layout.addWidget(item)
            # Reset indent to level 0 inside popup — popup items should
            # have only the base padding, matching top-level menu items.
            item.set_indent_level(0)
            # Nested groups inside a popup must use popup-based sub-menu
            # behaviour (hover → right-side popup) instead of inline
            # expand/collapse.  Hide the children wrapper and show a
            # right-pointing arrow so the group renders as a single row.
            if isinstance(item, TMenuItemGroup):
                item._children_wrapper.setVisible(False)
                item._arrow_label.setVisible(True)
                item._arrow_label.set_expanded(False)
                item._owner_group = self

        root_layout.addWidget(container)

        # Apply theme QSS to popup
        engine = ThemeEngine.instance()
        if engine.current_theme():
            try:
                qss = engine.render_qss("menu.qss.j2")
                popup.setStyleSheet(qss)
            except Exception:
                pass

        # Install event filter on both popup and container so that
        # Enter/Leave events from either widget cancel / start the
        # hide timer.  With WA_TranslucentBackground the transparent
        # shadow-margin area may not reliably propagate mouse events
        # on every platform, so listening on the container as well
        # ensures robust hover detection.
        popup.installEventFilter(self)
        container.installEventFilter(self)

        return popup


    def _apply_shadow_from_token(self, effect: QGraphicsDropShadowEffect) -> None:
        """Parse ``shadows.medium`` token and apply to *effect*.

        Token format: ``"<x>px <y>px <blur>px rgba(r,g,b,a)"``
        (e.g. ``"0 4px 16px rgba(0, 0, 0, 0.12)"``).

        Falls back to offset=(0,4), blur=16, color=rgba(0,0,0,0.12)
        on any parse failure.

        Args:
            effect: The QGraphicsDropShadowEffect to configure.
        """
        import re

        offset_x, offset_y, blur, color = 0, 4, 16, QColor(0, 0, 0, 31)
        try:
            engine = ThemeEngine.instance()
            raw = str(engine.get_token("shadows", "medium"))
            # Extract numeric values (strip optional "px" suffix)
            nums = [s.replace("px", "") for s in raw.split() if s[0].isdigit() or s[0] == "-"]
            if len(nums) >= 3:
                offset_x = int(nums[0])
                offset_y = int(nums[1])
                blur = int(nums[2])
            # Extract rgba color
            m = re.search(r"rgba?\([^)]+\)", raw)
            if m:
                color = parse_color(m.group(0))
        except Exception:
            pass

        effect.setOffset(offset_x, offset_y)
        effect.setBlurRadius(blur)
        effect.setColor(color)

    def _show_popup(self) -> None:
        """Show the popup widget, creating it if needed, and position it."""
        if self._popup is None:
            self._popup = self._create_popup()

        # Re-apply QSS to popup and refresh child item themes each time
        # so dark/light mode changes are picked up even if popup was cached
        engine = ThemeEngine.instance()
        if engine.current_theme():
            try:
                qss = engine.render_qss("menu.qss.j2")
                self._popup.setStyleSheet(qss)
            except Exception:
                pass
            for item in self._items:
                item.apply_theme()

        # Cancel any pending hide timer
        if self._hide_timer is not None:
            self._hide_timer.stop()

        popup = self._popup
        popup.adjustSize()

        # Read gap from Design Token (spacing.small), fallback to 4px
        try:
            gap = int(engine.get_token("spacing", "small"))
        except Exception:
            gap = 4

        # The popup has an 8px shadow margin around the visible container.
        # Subtract it so the *container* (not the transparent popup edge)
        # appears at the correct gap distance from the parent.
        shadow_margin = 8

        # Position: below header for top-level horizontal, right-side for
        # nested groups or collapsed vertical mode
        if self._is_nested_group() or self._collapsed_mode:
            global_pos = self.mapToGlobal(QPoint(self.width() + gap - shadow_margin, -shadow_margin))
        else:
            global_pos = self._header.mapToGlobal(
                QPoint(-shadow_margin, self._header.height() + gap - shadow_margin)
            )

        # Screen boundary check
        screen = QApplication.screenAt(global_pos)
        if screen is not None:
            avail = screen.availableGeometry()
            popup_size = popup.sizeHint()

            # Horizontal overflow
            if global_pos.x() + popup_size.width() > avail.right():
                if self._is_nested_group() or self._collapsed_mode:
                    global_pos.setX(
                        self.mapToGlobal(QPoint(0, 0)).x() - popup_size.width()
                    )
                else:
                    global_pos.setX(avail.right() - popup_size.width())

            # Vertical overflow
            if global_pos.y() + popup_size.height() > avail.bottom():
                global_pos.setY(avail.bottom() - popup_size.height())

        popup.move(global_pos)
        popup.show()


    def _hide_popup(self) -> None:
        """Hide the popup after a short delay (200ms)."""
        if self._popup is None:
            return

        if self._hide_timer is None:
            self._hide_timer = QTimer(self)
            self._hide_timer.setSingleShot(True)
            self._hide_timer.setInterval(200)
            self._hide_timer.timeout.connect(self._do_hide_popup)

        self._hide_timer.start()

    def _do_hide_popup(self) -> None:
        """Actually hide the popup widget.

        Checks both the outer popup and the inner container for mouse
        presence.  With WA_TranslucentBackground the outer popup's
        transparent shadow-margin may not reliably report underMouse()
        on all platforms, so the container check provides a safety net.

        Also keeps the popup open when a child group's sub-popup is
        visible — the user may be navigating a multi-level menu chain.
        """
        if self._popup is None:
            return
        try:
            if self._popup.underMouse():
                return
            container = self._popup.findChild(QWidget, "menu_popup_container")
            if container is not None and container.underMouse():
                return
        except RuntimeError:
            # C++ object already deleted during application shutdown
            return
        # Keep parent popup open while any child group's sub-popup is visible
        for item in self._items:
            if isinstance(item, TMenuItemGroup) and item._popup is not None and item._popup.isVisible():
                return
        # Cascade hide to any child group sub-popups before hiding ours
        for item in self._items:
            if isinstance(item, TMenuItemGroup) and item._popup is not None:
                item._popup.hide()
        self._popup.hide()
        # After hiding, notify the parent group (if any) to re-evaluate
        # its own popup visibility.  This handles the case where the mouse
        # left a deeply nested popup without passing through the parent.
        self._notify_parent_hide()

    def _should_use_popup(self) -> bool:
        """Return True when this group should show children via popup.

        This is the case in horizontal mode, collapsed mode, or when
        the group lives inside another group's popup container.
        """
        return self._is_horizontal_mode() or self._collapsed_mode or self._is_inside_popup()

    def _notify_parent_hide(self) -> None:
        """Ask the parent group to re-evaluate hiding its popup.

        When a nested group's popup hides, the parent group may also
        need to hide if the mouse is no longer over it.
        """
        if self._owner_group is not None:
            self._owner_group._hide_popup()

    def _is_inside_popup(self) -> bool:
        """Return True when this group is inside a popup container."""
        p = self.parent()
        while p is not None:
            if isinstance(p, _MenuPopupContainer):
                return True
            p = p.parent()  # type: ignore[assignment]
        return False

    def enterEvent(self, event: object) -> None:  # type: ignore[override]
        """Show popup on hover when in popup mode."""
        if self._should_use_popup() and not self._menu_disabled:
            self._show_popup()
        super().enterEvent(event)  # type: ignore[arg-type]

    def leaveEvent(self, event: object) -> None:  # type: ignore[override]
        """Start delayed popup hide on mouse leave when in popup mode."""
        if self._should_use_popup():
            self._hide_popup()
        super().leaveEvent(event)  # type: ignore[arg-type]

    def eventFilter(self, obj: object, event: object) -> bool:  # type: ignore[override]
        """Cancel popup hide when mouse enters the popup or its container."""
        from PySide6.QtCore import QEvent

        if self._popup is None or not hasattr(event, "type"):
            return False

        try:
            # Accept events from the outer popup *or* the inner container
            container = self._popup.findChild(QWidget, "menu_popup_container")
        except RuntimeError:
            # C++ object already deleted during application shutdown
            return False
        if obj is not self._popup and obj is not container:
            return False

        if event.type() == QEvent.Type.Enter:  # type: ignore[union-attr]
            # Mouse entered popup / container — cancel any pending hide
            if self._hide_timer is not None:
                self._hide_timer.stop()
        elif event.type() == QEvent.Type.Leave:  # type: ignore[union-attr]
            # Mouse left popup / container — start delayed hide
            self._hide_popup()
        return False


    def get_all_item_keys(self) -> list[str]:
        """Recursively collect all TMenuItem keys in this group.

        Returns:
            List of all descendant TMenuItem keys.
        """
        keys: list[str] = []
        for item in self._items:
            if isinstance(item, TMenuItem):
                keys.append(item.key)
            elif isinstance(item, TMenuItemGroup):
                keys.append(item.key)
                keys.extend(item.get_all_item_keys())
        return keys

    # -- Theme ----------------------------------------------------------------

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this group.

        Note: stylesheet is set by the parent TMenu. This method
        only triggers a re-polish to pick up token changes.
        Also re-applies QSS to the popup if it exists, updates
        the shadow effect parameters, and triggers a repaint of
        the inner container so background/border colors refresh.
        """
        self.style().unpolish(self)
        self.style().polish(self)
        # Propagate theme to arrow widget
        if hasattr(self, "_arrow_label"):
            self._arrow_label.apply_theme()
        # Re-apply theme to popup so it picks up dark/light token changes
        if self._popup is not None:
            engine = ThemeEngine.instance()
            if engine.current_theme():
                try:
                    qss = engine.render_qss("menu.qss.j2")
                    self._popup.setStyleSheet(qss)
                except Exception:
                    pass

            # Update shadow and repaint inner container for new theme tokens
            container = self._popup.findChild(QWidget, "menu_popup_container")
            if container is not None:
                effect = container.graphicsEffect()
                if isinstance(effect, QGraphicsDropShadowEffect):
                    self._apply_shadow_from_token(effect)
                container.update()


    # -- Events ---------------------------------------------------------------

    def set_menu_disabled(self, disabled: bool) -> None:
        """Set the menu-level disabled state, propagating to all children.

        Args:
            disabled: Whether the parent menu is disabled.
        """
        self._menu_disabled = disabled
        self.setProperty("groupDisabled", str(disabled).lower())
        self.setCursor(
            Qt.CursorShape.ForbiddenCursor if disabled
            else Qt.CursorShape.PointingHandCursor
        )
        self.style().unpolish(self)
        self.style().polish(self)
        for item in self._items:
            item.set_menu_disabled(disabled)

    def mousePressEvent(self, event: object) -> None:
        """Toggle expansion when the header is clicked (vertical mode only)."""
        if isinstance(event, QMouseEvent):
            if self._menu_disabled:
                return
            # In popup mode, interaction is handled by enter/leave events
            if self._should_use_popup():
                return
            header_rect = self._header.geometry()
            if header_rect.contains(event.pos()):
                self.set_expanded(not self._expanded)
                return
        super().mousePressEvent(event)  # type: ignore[arg-type]

    # -- Private --------------------------------------------------------------

    def _update_arrow(self) -> None:
        """Update the arrow indicator based on expanded state."""
        self._arrow_label.set_expanded(self._expanded)

    def _apply_indent_to_children(self) -> None:
        """Recursively apply indentation to all children."""
        child_level = self._indent_level + 1
        for item in self._items:
            if isinstance(item, TMenuItem):
                item.set_indent_level(child_level)
            elif isinstance(item, TMenuItemGroup):
                item.set_indent_level(child_level)

    def _animate_toggle(self, expanding: bool) -> None:
        """Run the expand/collapse animation (200ms ease-in-out).

        Args:
            expanding: True if expanding, False if collapsing.
        """
        self._animating = True

        if expanding:
            self._children_wrapper.setVisible(True)
            self._children_wrapper.setMaximumHeight(16777215)
            target_height = self._children_wrapper.sizeHint().height()
            self._children_wrapper.setMaximumHeight(0)
        else:
            target_height = 0

        start_height = self._children_wrapper.maximumHeight() if not expanding else 0

        anim = QPropertyAnimation(self._children_wrapper, b"maximumHeight", self)
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
        self._children_wrapper.setMaximumHeight(16777215)

    def _on_collapse_finished(self) -> None:
        """Called when collapse animation completes."""
        self._animating = False
        self._children_wrapper.setVisible(False)


class TMenu(BaseWidget):
    """Navigation menu supporting vertical/horizontal mode and multi-level nesting.

    Features route awareness for automatic active item highlighting,
    collapsed mode showing only icons, and disabled state.

    Args:
        mode: Layout mode (vertical or horizontal).
        active_key: Key of the initially active item.
        collapsed: Whether the menu starts in collapsed (icon-only) mode.
        route_awareness: Whether to auto-match active item from route path.
        disabled: Whether the entire menu is disabled.
        parent: Optional parent widget.

    Signals:
        item_selected: Emitted with the selected item's key.

    Example:
        >>> menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        >>> menu.add_item(TMenuItem(key="home", label="Home"))
        >>> menu.add_item(TMenuItem(key="about", label="About"))
        >>> menu.set_active_key("home")
    """

    class MenuMode(str, Enum):
        """Menu layout mode."""

        VERTICAL = "vertical"
        HORIZONTAL = "horizontal"

    item_selected = Signal(str, object)
    expanded_keys_changed = Signal(list)

    _COLLAPSE_ANIMATION_DURATION = 200

    def __init__(
        self,
        mode: MenuMode = MenuMode.VERTICAL,
        active_key: str = "",
        collapsed: bool = False,
        route_awareness: bool = False,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        self._mode = mode
        self._active_key = active_key
        self._collapsed = collapsed
        self._route_awareness = route_awareness
        self._disabled = disabled
        self._items: list[TMenuItem | TMenuItemGroup] = []
        self._width_anim: QPropertyAnimation | None = None
        self._width_anim_max: QPropertyAnimation | None = None
        self._menu_bg_color: str | None = None

        super().__init__(parent)

        # Enable QSS background-color rendering for this custom widget
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Create collapse toggle button (before _build_ui so it exists for layout)
        self._collapse_toggle = _CollapseToggleButton(self)
        self._collapse_toggle._menu_ref = self
        self._collapse_toggle.clicked.connect(
            lambda: self.set_collapsed(not self._collapsed)
        )

        self.setProperty("mode", mode.value)
        self.setProperty("disabled", str(disabled).lower())

        self._build_ui()
        self.apply_theme()

        # Hide all popups when the application loses focus so they
        # don't float above other windows.
        app = QApplication.instance()
        if app is not None:
            app.focusChanged.connect(self._on_app_focus_changed)  # type: ignore[union-attr]

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the menu layout based on mode."""
        if self._mode == self.MenuMode.HORIZONTAL:
            self._root_layout = QHBoxLayout(self)
            # Horizontal menu: fixed height to menu items only
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        else:
            self._root_layout = QVBoxLayout(self)
            # Vertical menu: expand to fill parent container height
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        if self._mode == self.MenuMode.VERTICAL:
            self._root_layout.addStretch()

        # Sync toggle button initial state and visibility
        if self._collapsed:
            self._collapse_toggle.set_collapsed(True)
        self._update_toggle_visibility()
        # Ensure toggle button paints above menu items
        self._collapse_toggle.raise_()

    # -- Public API -----------------------------------------------------------

    @property
    def mode(self) -> MenuMode:
        """Return the current menu layout mode."""
        return self._mode

    def set_mode(self, mode: MenuMode) -> None:
        """Switch the menu layout mode at runtime.

        Rebuilds the root layout and re-adds all existing items
        under the new mode. Propagates the mode change to all
        TMenuItemGroup children.

        Args:
            mode: The new MenuMode to apply.
        """
        if mode == self._mode:
            return
        self._mode = mode
        self.setProperty("mode", mode.value)

        # Clear fixed width constraints when switching to horizontal
        if self._mode == self.MenuMode.HORIZONTAL:
            # Uncollapse if currently collapsed (collapsed is vertical-only)
            if self._collapsed:
                self._collapsed = False
                for item in self._items:
                    item.set_collapsed_mode(False)
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)

        # Detach all item widgets from the current layout (without deleting).
        # We must NOT call setParent(None) because PySide6 may destroy the
        # underlying C++ object when the parent is cleared.  Instead we
        # just take items out of the layout and keep them parented to self.
        while self._root_layout.count():
            self._root_layout.takeAt(0)

        # Remove the old layout by transferring it to a temporary widget.
        QWidget().setLayout(self._root_layout)

        # Rebuild layout for the new mode
        if self._mode == self.MenuMode.HORIZONTAL:
            self._root_layout = QHBoxLayout(self)
            # Horizontal menu: fixed height to menu items only
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        else:
            self._root_layout = QVBoxLayout(self)
            # Vertical menu: expand to fill parent container height
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        if self._mode == self.MenuMode.VERTICAL:
            self._root_layout.addStretch()

        # Re-add all items under the new layout
        is_horiz = self._mode == self.MenuMode.HORIZONTAL
        for item in self._items:
            item.setParent(self)
            if self._mode == self.MenuMode.VERTICAL:
                idx = self._root_layout.count() - 1
                if idx < 0:
                    idx = 0
                self._root_layout.insertWidget(idx, item)
            else:
                self._root_layout.addWidget(item)

            # Propagate mode to groups
            if isinstance(item, TMenuItemGroup):
                item.set_menu_mode(self._mode)

            # Adjust item margins for horizontal/vertical mode
            if isinstance(item, TMenuItem):
                item.set_horizontal_layout(is_horiz)

        # Re-apply theme so QSS ancestor selectors (TMenu[mode=...]) take effect
        self.apply_theme()

        # Update toggle button visibility based on new mode
        self._update_toggle_visibility()

    @property
    def collapsed(self) -> bool:
        """Return whether the menu is in collapsed (icon-only) mode."""
        return self._collapsed

    @property
    def route_awareness(self) -> bool:
        """Return whether route awareness is enabled."""
        return self._route_awareness

    @property
    def disabled(self) -> bool:
        """Return whether the entire menu is disabled."""
        return self._disabled

    def add_item(self, item: TMenuItem | TMenuItemGroup) -> None:
        """Add a top-level menu item or group.

        Args:
            item: TMenuItem or TMenuItemGroup to add.
        """
        self._items.append(item)
        item.setParent(self)

        # Insert before the stretch (for vertical mode)
        if self._mode == self.MenuMode.VERTICAL:
            idx = self._root_layout.count() - 1  # before stretch
            if idx < 0:
                idx = 0
            self._root_layout.insertWidget(idx, item)
        else:
            self._root_layout.addWidget(item)

        # Connect item clicked signals
        self._connect_item_signals(item)

        # Propagate menu mode to groups
        if isinstance(item, TMenuItemGroup):
            item.set_menu_mode(self._mode)

        # Adjust item margins for horizontal/vertical mode
        is_horiz = self._mode == self.MenuMode.HORIZONTAL
        if isinstance(item, TMenuItem):
            item.set_horizontal_layout(is_horiz)

        # Apply collapsed mode if active
        if self._collapsed:
            item.set_collapsed_mode(True)

        # Apply active key if set
        if self._active_key:
            self._apply_active_key_to_item(item, self._active_key)

        # Apply disabled state if menu is disabled
        if self._disabled:
            item.set_menu_disabled(True)

    def set_active_key(self, key: str) -> None:
        """Set the currently active (highlighted) menu item by key.

        Args:
            key: The key of the item to activate.
        """
        self._active_key = key
        self._apply_active_key_recursive(self._items, key)

    def get_active_key(self) -> str:
        """Return the key of the currently active item."""
        return self._active_key

    def set_collapsed(self, collapsed: bool) -> None:
        """Set the collapsed (icon-only) mode with width animation.

        Collapsed mode only applies to vertical menus. In horizontal
        mode this method is a no-op.

        Args:
            collapsed: Whether to collapse the menu.
        """
        if collapsed == self._collapsed:
            return
        # Collapsed mode is vertical-only (matches NaiveUI behavior)
        if self._mode == self.MenuMode.HORIZONTAL:
            self._collapsed = False
            return
        self._collapsed = collapsed

        if collapsed:
            # When collapsing: animate width first, then switch item display
            # after animation completes so icons don't jump during transition.
            self._animate_collapse(True)
        else:
            # When expanding: switch item display first, then animate width
            for item in self._items:
                item.set_collapsed_mode(False)
            self._animate_collapse(False)

        # Sync toggle button state
        self._collapse_toggle.set_collapsed(collapsed)

    def set_route(self, path: str) -> None:
        """Set current route path for automatic active item matching.

        Searches all TMenuItem keys for the best match against the path.
        If no match is found, the active key remains unchanged.

        Args:
            path: Route path string to match against item keys.
        """
        if not self._route_awareness:
            return

        best_key = self._find_matching_key(path)
        if best_key:
            self.set_active_key(best_key)

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable the entire menu, propagating to all children.

        Args:
            disabled: Whether to disable all interactions.
        """
        self._disabled = disabled
        self.setProperty("disabled", str(disabled).lower())
        self.setCursor(
            Qt.CursorShape.ForbiddenCursor if disabled
            else Qt.CursorShape.ArrowCursor
        )
        self.style().unpolish(self)
        self.style().polish(self)
        for item in self._items:
            item.set_menu_disabled(disabled)

        # Sync toggle button disabled state
        self._collapse_toggle.set_disabled(disabled)

    # -- Theme ----------------------------------------------------------------

    def apply_theme(self) -> None:
        """Apply the current theme to this menu.

        Stores the background color from tokens and triggers a repaint.
        The background is drawn in paintEvent to bypass QSS conflicts
        with parent containers (e.g. Playground preview panel).
        """
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        self._menu_bg_color = str(engine.get_token("colors", "bg_default"))
        self.update()

        # Propagate theme to toggle button (guard for init order:
        # BaseWidget.__init__ calls apply_theme before _collapse_toggle exists)
        if hasattr(self, "_collapse_toggle"):
            self._collapse_toggle.apply_theme()

    def paintEvent(self, event: object) -> None:
        """Paint the menu background manually to bypass QSS conflicts."""
        painter = QPainter(self)
        bg = getattr(self, "_menu_bg_color", None)
        if bg:
            painter.fillRect(self.rect(), parse_color(bg))
        painter.end()
        # Ensure the collapse toggle stays above the menu background.
        # Because the toggle is reparented to menu_parent (a sibling),
        # each menu repaint can cover the toggle's overlapping portion.
        if hasattr(self, "_collapse_toggle") and self._collapse_toggle.isVisible():
            self._collapse_toggle.raise_()

    def resizeEvent(self, event: object) -> None:  # type: ignore[override]
        """Reposition toggle button when menu is resized."""
        super().resizeEvent(event)  # type: ignore[arg-type]
        if hasattr(self, "_collapse_toggle"):
            self._collapse_toggle.reposition()

    def showEvent(self, event: object) -> None:  # type: ignore[override]
        """Reparent and reposition toggle button when menu becomes visible."""
        super().showEvent(event)  # type: ignore[arg-type]
        if hasattr(self, "_collapse_toggle"):
            self._collapse_toggle.reposition()

    # -- Private --------------------------------------------------------------

    def _connect_item_signals(self, item: TMenuItem | TMenuItemGroup) -> None:
        """Recursively connect clicked signals from all descendant items.

        Args:
            item: Item or group to connect.
        """
        if isinstance(item, TMenuItem):
            item.clicked.connect(self._on_item_clicked)
        elif isinstance(item, TMenuItemGroup):
            item.expanded_changed.connect(self._on_group_expanded_changed)
            for child in item.get_items():
                self._connect_item_signals(child)

    def _on_item_clicked(self, key: str) -> None:
        """Handle a menu item click.

        Args:
            key: The key of the clicked item.
        """
        if self._disabled:
            return
        self.set_active_key(key)
        # Find the item to build MenuOption
        option = MenuOption(key=key)
        item = self._find_item_by_key(key)
        if item is not None and isinstance(item, TMenuItem):
            option = MenuOption(key=key, label=item.label)
        self.item_selected.emit(key, option)
        self._emit_bus_event("item_selected", key, option)
        # Close all popup chains after selection
        self._hide_all_popups()

    def _find_item_by_key(self, key: str) -> TMenuItem | None:
        """Find a TMenuItem by key in the item tree.

        Args:
            key: The key to search for.

        Returns:
            The matching TMenuItem or None.
        """
        for item in self._items:
            if isinstance(item, TMenuItem) and item.key == key:
                return item
            if isinstance(item, TMenuItemGroup):
                found = self._find_item_in_group(item, key)
                if found is not None:
                    return found
        return None

    def _find_item_in_group(self, group: TMenuItemGroup, key: str) -> TMenuItem | None:
        """Recursively find a TMenuItem in a group.

        Args:
            group: The group to search.
            key: The key to search for.

        Returns:
            The matching TMenuItem or None.
        """
        for child in group.get_items():
            if isinstance(child, TMenuItem) and child.key == key:
                return child
            if isinstance(child, TMenuItemGroup):
                found = self._find_item_in_group(child, key)
                if found is not None:
                    return found
        return None

    def _collect_expanded_keys(self) -> list[str]:
        """Collect all expanded group keys.

        Returns:
            List of expanded group key strings.
        """
        keys: list[str] = []
        for item in self._items:
            if isinstance(item, TMenuItemGroup):
                self._collect_expanded_keys_recursive(item, keys)
        return keys

    def _collect_expanded_keys_recursive(
        self, group: TMenuItemGroup, keys: list[str]
    ) -> None:
        """Recursively collect expanded group keys.

        Args:
            group: The group to check.
            keys: Accumulator list.
        """
        if group.is_expanded:
            keys.append(group.key)
        for child in group.get_items():
            if isinstance(child, TMenuItemGroup):
                self._collect_expanded_keys_recursive(child, keys)

    def _on_group_expanded_changed(self, _expanded: bool) -> None:
        """Handle a group's expanded state change to emit expanded_keys_changed."""
        keys = self._collect_expanded_keys()
        self.expanded_keys_changed.emit(keys)
        self._emit_bus_event("expanded_keys_changed", keys)

    def _apply_active_key_recursive(
        self, items: list[TMenuItem | TMenuItemGroup], key: str
    ) -> None:
        """Recursively set active state on all items.

        Args:
            items: List of items to update.
            key: The key to activate.
        """
        for item in items:
            if isinstance(item, TMenuItem):
                item.set_active(item.key == key)
            elif isinstance(item, TMenuItemGroup):
                self._apply_active_key_recursive(item.get_items(), key)

    def _apply_active_key_to_item(
        self, item: TMenuItem | TMenuItemGroup, key: str
    ) -> None:
        """Apply active key to a single item or group.

        Args:
            item: Item or group to update.
            key: The key to activate.
        """
        if isinstance(item, TMenuItem):
            item.set_active(item.key == key)
        elif isinstance(item, TMenuItemGroup):
            self._apply_active_key_recursive(item.get_items(), key)

    def _find_matching_key(self, path: str) -> str:
        """Find the best matching item key for a route path.

        Uses longest-prefix matching: the item key that is the longest
        prefix of (or equal to) the path wins.

        Args:
            path: Route path to match.

        Returns:
            The best matching key, or empty string if no match.
        """
        all_keys = self._collect_all_keys(self._items)
        best = ""
        for k in all_keys:
            if path == k or path.startswith(k + "/") or path.startswith(k):
                if len(k) > len(best):
                    best = k
        return best

    def _collect_all_keys(self, items: list[TMenuItem | TMenuItemGroup]) -> list[str]:
        """Recursively collect all TMenuItem keys.

        Args:
            items: Items to scan.

        Returns:
            List of all item keys.
        """
        keys: list[str] = []
        for item in items:
            if isinstance(item, TMenuItem):
                keys.append(item.key)
            elif isinstance(item, TMenuItemGroup):
                keys.extend(self._collect_all_keys(item.get_items()))
        return keys

    def _update_toggle_visibility(self) -> None:
        """Show toggle button only in vertical mode."""
        visible = self._mode == self.MenuMode.VERTICAL
        self._collapse_toggle.setVisible(visible)
        if visible:
            self._collapse_toggle.reposition()

    def _animate_collapse(self, collapsing: bool) -> None:
        """Animate the menu width for collapse/expand transition.

        Args:
            collapsing: True if collapsing, False if expanding.
        """
        engine = ThemeEngine.instance()
        collapsed_width = 48
        if engine.current_theme():
            tokens = engine.current_tokens()
            if tokens and tokens.menu:
                collapsed_width = tokens.menu.get("collapsed_width", 48)

        # Stop any running animations
        if self._width_anim is not None:
            self._width_anim.stop()
        if self._width_anim_max is not None:
            self._width_anim_max.stop()

        current_width = self.width()

        if collapsing:
            # Remember expanded width for later restore
            self._expanded_width = current_width
            target = collapsed_width
        else:
            target = getattr(self, "_expanded_width", 220)

        if not self.isVisible():
            if collapsing:
                self.setFixedWidth(target)
                # Apply collapsed mode immediately when not visible
                for item in self._items:
                    item.set_collapsed_mode(True)
            else:
                self.setFixedWidth(target)
            return

        self._width_anim = QPropertyAnimation(self, b"minimumWidth", self)
        self._width_anim.setDuration(self._COLLAPSE_ANIMATION_DURATION)
        self._width_anim.setStartValue(current_width)
        self._width_anim.setEndValue(target)
        self._width_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._width_anim_max = QPropertyAnimation(self, b"maximumWidth", self)
        self._width_anim_max.setDuration(self._COLLAPSE_ANIMATION_DURATION)
        self._width_anim_max.setStartValue(current_width)
        self._width_anim_max.setEndValue(target)
        self._width_anim_max.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if collapsing:
            # Switch to icon-only mode after animation finishes
            self._width_anim.finished.connect(self._on_collapse_finished)

        self._width_anim.start()
        self._width_anim_max.start()

    def _on_collapse_finished(self) -> None:
        """Apply collapsed mode to items after the collapse animation ends."""
        for item in self._items:
            item.set_collapsed_mode(True)

    def _hide_all_popups(self) -> None:
        """Recursively hide all popup chains in this menu."""
        for item in self._items:
            if isinstance(item, TMenuItemGroup):
                self._hide_popups_recursive(item)

    def _hide_popups_recursive(self, group: TMenuItemGroup) -> None:
        """Hide popup for a group and all its nested sub-groups."""
        if group._popup is not None and group._popup.isVisible():
            group._popup.hide()
        if group._hide_timer is not None:
            group._hide_timer.stop()
        for child in group._items:
            if isinstance(child, TMenuItemGroup):
                self._hide_popups_recursive(child)

    def _on_app_focus_changed(self, _old: QWidget | None, now: QWidget | None) -> None:
        """Hide all popups when the application loses focus."""
        if now is None:
            self._hide_all_popups()
