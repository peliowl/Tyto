"""Back-to-top button component.

Monitors a target QScrollArea and provides a floating button that appears
when the scroll position exceeds a configurable threshold. Clicking the
button smoothly scrolls back to the top using the EasingEngine.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Union

from PySide6.QtCore import QEvent, QObject, QPointF, QRectF, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QGraphicsOpacityEffect,
    QLabel,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.easing_engine import EasingEngine
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color

# Scroll animation duration in milliseconds.
_SCROLL_DURATION_MS = 300

# Animation tick interval in milliseconds.
_TICK_INTERVAL_MS = 16

# Button diameter
_BUTTON_SIZE = 40

# Type alias for listen_to parameter.
ListenToType = Union[str, QWidget, Callable[[], QWidget], None]


class TBackTop(BaseWidget):
    """Back-to-top button that appears when scroll exceeds threshold.

    Monitors a target QAbstractScrollArea and provides smooth linear
    scroll animation back to top.

    Args:
        target: Scroll area to monitor. Can be set later via set_target().
        visibility_height: Scroll distance threshold to show the button.
        right: Distance from the right edge of the target in pixels.
        bottom: Distance from the bottom edge of the target in pixels.
        show: Controlled visibility mode. None = auto (default), True/False = forced.
        to: Render target container (teleport). None = render in parent.
        listen_to: Scroll event source. String (objectName), QWidget, or Callable.
        parent: Optional parent widget.

    Signals:
        clicked: Emitted when the back-to-top button is clicked.
        visibility_changed: Emitted when show/hide state changes, carries bool.

    Example:
        >>> scroll = QScrollArea()
        >>> backtop = TBackTop(target=scroll)
        >>> backtop.clicked.connect(lambda: print("scrolled to top"))
    """

    clicked = Signal()
    visibility_changed = Signal(bool)
    shown = Signal()
    hidden = Signal()

    def __init__(
        self,
        target: QAbstractScrollArea | None = None,
        visibility_height: int = 200,
        right: int = 40,
        bottom: int = 40,
        show: bool | None = None,
        to: QWidget | None = None,
        listen_to: ListenToType = None,
        parent: QWidget | None = None,
    ) -> None:
        self._target: QAbstractScrollArea | None = None
        self._visibility_height = visibility_height
        self._right = right
        self._bottom = bottom
        self._show: bool | None = show
        self._to: QWidget | None = to
        self._listen_to: ListenToType = listen_to
        self._listen_target: QAbstractScrollArea | None = None
        self._custom_content: QWidget | None = None
        self._is_visible_state: bool = False

        super().__init__(parent)

        # Scroll animation state
        self._scroll_start: int = 0
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(_TICK_INTERVAL_MS)
        self._scroll_timer.timeout.connect(self._on_scroll_tick)
        self._scroll_elapsed: int = 0
        self._easing = EasingEngine.ease_out_cubic

        # Fade animation state
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(_TICK_INTERVAL_MS)
        self._fade_timer.timeout.connect(self._on_fade_tick)
        self._fade_target: float = 0.0
        self._fade_current: float = 0.0

        self.setGraphicsEffect(self._opacity_effect)
        self.setFixedSize(_BUTTON_SIZE + 12, _BUTTON_SIZE + 12)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

        self._default_label: QLabel | None = None
        self._content_container: QWidget | None = None

        if target is not None:
            self.set_target(target)

        # Apply controlled mode if set
        if self._show is not None:
            self._apply_controlled_visibility(self._show)

    # -- Public API -----------------------------------------------------------

    @property
    def visibility_height(self) -> int:
        """Return the scroll threshold for showing the button."""
        return self._visibility_height

    @visibility_height.setter
    def visibility_height(self, value: int) -> None:
        """Set the scroll threshold and re-evaluate current visibility.

        Args:
            value: New threshold in pixels.
        """
        self._visibility_height = value
        if self._target is not None:
            vbar = self._target.verticalScrollBar()
            if vbar is not None:
                self._on_scroll_changed(vbar.value())

    @property
    def right_offset(self) -> int:
        """Return the right edge offset in pixels."""
        return self._right

    @property
    def bottom_offset(self) -> int:
        """Return the bottom edge offset in pixels."""
        return self._bottom

    @property
    def controlled_show(self) -> bool | None:
        """Return the controlled visibility mode.

        None means auto mode (default), True/False means forced show/hide.
        """
        return self._show

    @controlled_show.setter
    def controlled_show(self, value: bool | None) -> None:
        """Set the controlled visibility mode.

        Args:
            value: None for auto mode, True to force show, False to force hide.
        """
        self._show = value
        if value is not None:
            self._apply_controlled_visibility(value)
        elif self._target is not None:
            # Revert to auto mode — re-evaluate from scroll position
            vbar = self._target.verticalScrollBar()
            if vbar is not None:
                self._on_scroll_changed(vbar.value())

    @property
    def to(self) -> QWidget | None:
        """Return the render target container."""
        return self._to

    def set_to(self, widget: QWidget | None) -> None:
        """Set the render target container (teleport).

        Args:
            widget: Target container widget, or None to render in parent.
        """
        self._to = widget
        if widget is not None:
            self.setParent(widget)  # type: ignore[call-overload]
        elif self._target is not None:
            self.setParent(self._target)  # type: ignore[call-overload]

    @property
    def listen_to_value(self) -> ListenToType:
        """Return the current listen_to configuration."""
        return self._listen_to

    def set_listen_to(self, value: ListenToType) -> None:
        """Set the scroll event source.

        Args:
            value: String (objectName), QWidget instance, Callable returning QWidget, or None.
        """
        self._disconnect_listen_target()
        self._listen_to = value
        self._resolve_and_connect_listen_to()

    def set_target(self, target: QAbstractScrollArea) -> None:
        """Set the scroll area to monitor.

        Disconnects from any previous target and connects to the new one.

        Args:
            target: The QAbstractScrollArea to monitor.
        """
        # Disconnect old target
        if self._target is not None:
            try:
                self._target.removeEventFilter(self)
                vbar = self._target.verticalScrollBar()
                if vbar is not None:
                    vbar.valueChanged.disconnect(self._on_scroll_changed)
            except (RuntimeError, TypeError):
                pass

        self._target = target

        # Set parent based on 'to' property
        if self._to is not None:
            self.setParent(self._to)  # type: ignore[call-overload]
        else:
            self.setParent(target)  # type: ignore[call-overload]

        # Install event filter to track target resize
        target.installEventFilter(self)

        # Resolve listen_to or fall back to target
        if self._listen_to is not None:
            self._resolve_and_connect_listen_to()
        else:
            vbar = target.verticalScrollBar()
            if vbar is not None:
                vbar.valueChanged.connect(self._on_scroll_changed)
            self._on_scroll_changed(vbar.value() if vbar else 0)

        self._update_position()

    def set_content(self, widget: QWidget) -> None:
        """Set custom button content, replacing the default arrow icon.

        Note: custom content is not rendered in the painted mode.
        This method is kept for API compatibility.

        Args:
            widget: Widget to display inside the button.
        """
        self._custom_content = widget

    # -- Qt event overrides ---------------------------------------------------

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the circular button with shadow and arrow icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        r = _BUTTON_SIZE / 2.0

        try:
            engine = ThemeEngine.instance()
            theme = engine.current_theme() or "light"
            if theme == "dark":
                bg_color = QColor("#48484e")
                icon_color = QColor(255, 255, 255, 210)
            else:
                bg_color = parse_color(str(engine.get_token("colors", "bg_default")))
                icon_color = parse_color(str(engine.get_token("colors", "text_primary")))
        except Exception:
            bg_color = QColor("#ffffff")
            icon_color = QColor("#333639")
            theme = "light"

        painter.setPen(Qt.PenStyle.NoPen)
        if theme != "dark":
            for i in range(4):
                shadow_r = r + 4 - i
                shadow_color = QColor(0, 0, 0, 8 + i * 3)
                painter.setBrush(shadow_color)
                painter.drawEllipse(QRectF(cx - shadow_r, cy - shadow_r + 1, shadow_r * 2, shadow_r * 2))

        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        pen = QPen(icon_color)
        pen.setWidthF(2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        line_half = 6.0
        line_y = cy - 6.0
        painter.drawLine(QPointF(cx - line_half, line_y), QPointF(cx + line_half, line_y))

        arrow_top = cy - 3.0
        arrow_bottom = cy + 7.0
        painter.drawLine(QPointF(cx, arrow_top), QPointF(cx, arrow_bottom))

        head_size = 4.0
        painter.drawLine(QPointF(cx - head_size, arrow_top + head_size), QPointF(cx, arrow_top))
        painter.drawLine(QPointF(cx + head_size, arrow_top + head_size), QPointF(cx, arrow_top))

        painter.end()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Reposition the button when the target scroll area is resized."""
        if hasattr(self, "_target") and obj is self._target and event.type() == QEvent.Type.Resize:
            self._update_position()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event: object) -> None:  # noqa: N802
        """Handle mouse press to trigger scroll-to-top."""
        self.clicked.emit()
        self._scroll_to_top()

    # -- Private helpers ------------------------------------------------------

    def _apply_controlled_visibility(self, visible: bool) -> None:
        """Apply forced show/hide in controlled mode and emit signal."""
        if visible:
            self._fade_in()
        else:
            self._fade_out()
        self._set_visible_state(visible)

    def _set_visible_state(self, visible: bool) -> None:
        """Update internal visibility state and emit signal if changed."""
        if visible != self._is_visible_state:
            self._is_visible_state = visible
            self.visibility_changed.emit(visible)
            self._emit_bus_event("visibility_changed", visible)
            if visible:
                self.shown.emit()
                self._emit_bus_event("shown")
            else:
                self.hidden.emit()
                self._emit_bus_event("hidden")

    def _on_scroll_changed(self, value: int) -> None:
        """React to scroll position changes."""
        if self._show is not None:
            return
        should_show = value >= self._visibility_height
        if should_show:
            self._fade_in()
        else:
            self._fade_out()
        self._set_visible_state(should_show)
        self._update_position()

    def _resolve_and_connect_listen_to(self) -> None:
        """Resolve the listen_to value and connect to its scroll bar."""
        resolved: QWidget | None = None

        if isinstance(self._listen_to, str):
            parent = self.parent()
            if parent is not None:
                found = parent.findChild(QAbstractScrollArea, self._listen_to)  # type: ignore[arg-type]
                if isinstance(found, QAbstractScrollArea):
                    resolved = found
        elif isinstance(self._listen_to, QWidget):
            resolved = self._listen_to
        elif callable(self._listen_to):
            try:
                resolved = self._listen_to()
            except Exception:
                resolved = None

        if isinstance(resolved, QAbstractScrollArea):
            self._listen_target = resolved
            vbar = resolved.verticalScrollBar()
            if vbar is not None:
                vbar.valueChanged.connect(self._on_scroll_changed)
                self._on_scroll_changed(vbar.value())

    def _disconnect_listen_target(self) -> None:
        """Disconnect from the current listen target's scroll bar."""
        if self._listen_target is not None:
            try:
                vbar = self._listen_target.verticalScrollBar()
                if vbar is not None:
                    vbar.valueChanged.disconnect(self._on_scroll_changed)
            except (RuntimeError, TypeError):
                pass
            self._listen_target = None

    def _update_position(self) -> None:
        """Position the button relative to the target scroll area."""
        if self._target is None:
            return
        # Use the scroll area's own size (button is a child of the scroll area)
        tw = self._target.width()
        th = self._target.height()
        x = tw - self.width() - self._right
        y = th - self.height() - self._bottom
        self.move(max(0, x), max(0, y))
        self.raise_()

    def _fade_in(self) -> None:
        """Fade the button in."""
        if self._fade_target == 1.0 and self.isVisible():
            return
        self._fade_target = 1.0
        self.show()
        self._fade_timer.start()

    def _fade_out(self) -> None:
        """Fade the button out."""
        if self._fade_target == 0.0 and not self.isVisible():
            return
        self._fade_target = 0.0
        self._fade_timer.start()

    def _on_fade_tick(self) -> None:
        """Advance the fade animation by one tick."""
        step = 0.1
        if self._fade_target > self._fade_current:
            self._fade_current = min(self._fade_current + step, 1.0)
        else:
            self._fade_current = max(self._fade_current - step, 0.0)

        self._opacity_effect.setOpacity(self._fade_current)

        if self._fade_current == self._fade_target:
            self._fade_timer.stop()
            if self._fade_current == 0.0:
                self.hide()

    def _scroll_to_top(self) -> None:
        """Start smooth scroll animation to top."""
        if self._target is None:
            return
        vbar = self._target.verticalScrollBar()
        if vbar is None:
            return
        self._scroll_start = vbar.value()
        if self._scroll_start == 0:
            return
        self._scroll_elapsed = 0
        self._scroll_timer.start()

    def _on_scroll_tick(self) -> None:
        """Advance the scroll animation by one tick."""
        if self._target is None:
            self._scroll_timer.stop()
            return

        vbar = self._target.verticalScrollBar()
        if vbar is None:
            self._scroll_timer.stop()
            return

        self._scroll_elapsed += _TICK_INTERVAL_MS
        t = min(self._scroll_elapsed / _SCROLL_DURATION_MS, 1.0)
        progress = self._easing(t)
        new_value = int(self._scroll_start * (1.0 - progress))
        vbar.setValue(new_value)

        if t >= 1.0:
            self._scroll_timer.stop()
            vbar.setValue(0)

    def apply_theme(self) -> None:
        """Update styles from current theme tokens."""
        engine = ThemeEngine.instance()
        try:
            qss = engine.render_qss("backtop.qss.j2")
            self.setStyleSheet(qss)
        except RuntimeError:
            pass

    def cleanup(self) -> None:
        """Stop timers and disconnect signals before destruction."""
        self._scroll_timer.stop()
        self._fade_timer.stop()
        self._disconnect_listen_target()
        if self._target is not None:
            try:
                self._target.removeEventFilter(self)
                vbar = self._target.verticalScrollBar()
                if vbar is not None:
                    vbar.valueChanged.disconnect(self._on_scroll_changed)
            except (RuntimeError, TypeError):
                pass
        super().cleanup()
