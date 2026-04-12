"""TSlider atom component: a NaiveUI-style slider with single and range modes.

Supports single-thumb and dual-thumb (range) selection, step snapping,
marks/labels, tooltip display, vertical orientation, disabled state,
reverse direction, keyboard control, tooltip placement, and mark-snap mode.
Emits ``value_changed``, ``drag_start``, and ``drag_end`` signals.
"""

from __future__ import annotations

from typing import Any, Union

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QKeyEvent, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color

# Type alias for slider value: single number or range tuple
SliderValue = Union[int, float, tuple[Union[int, float], Union[int, float]]]

# Fallback dimensions when tokens are unavailable
_FALLBACK_TRACK_HEIGHT = 4
_FALLBACK_THUMB_SIZE = 14
_FALLBACK_THUMB_BORDER = 2


def _get_slider_dims() -> dict[str, int]:
    """Retrieve slider dimensions from ThemeEngine tokens or fallback."""
    try:
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens and tokens.slider:
            return tokens.slider
    except (RuntimeError, KeyError):
        pass
    return {
        "track_height": _FALLBACK_TRACK_HEIGHT,
        "thumb_size": _FALLBACK_THUMB_SIZE,
        "thumb_border_size": _FALLBACK_THUMB_BORDER,
    }


def _snap_to_step(value: float, min_val: float, max_val: float, step: float) -> float:
    """Snap a value to the nearest step within [min_val, max_val]."""
    if step <= 0:
        return max(min_val, min(value, max_val))
    steps_from_min = round((value - min_val) / step)
    snapped = min_val + steps_from_min * step
    return max(min_val, min(snapped, max_val))


def _get_color(category: str, key: str, fallback: str) -> QColor:
    """Safely retrieve a color token, returning fallback on failure."""
    try:
        engine = ThemeEngine.instance()
        return parse_color(str(engine.get_token(category, key)), fallback)
    except (RuntimeError, KeyError):
        return parse_color(fallback)


class _SliderTrack(QWidget):
    """Internal widget that paints the slider track, filled region, and thumbs.

    Handles mouse interaction for dragging thumbs and clicking on the track.
    """

    # Emitted when the user changes a thumb position via mouse interaction
    thumb_moved = Signal()
    # Emitted when the user starts/ends dragging a thumb
    drag_started = Signal()
    drag_ended = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("slider_track")
        self.setMouseTracking(True)

        # Slider state
        self._min: float = 0.0
        self._max: float = 100.0
        self._step: float = 1.0
        self._range_mode: bool = False
        self._vertical: bool = False
        self._disabled: bool = False
        self._reverse: bool = False
        self._mark_snap: bool = False  # step="mark" mode

        # Thumb positions as normalised fractions [0, 1]
        self._thumb_pos: float = 0.0  # single mode or low thumb in range
        self._thumb_pos_high: float = 1.0  # high thumb in range mode

        # Dimensions from tokens
        dims = _get_slider_dims()
        self._track_h: int = dims.get("track_height", _FALLBACK_TRACK_HEIGHT)
        self._thumb_d: int = dims.get("thumb_size", _FALLBACK_THUMB_SIZE)
        self._thumb_border: int = dims.get("thumb_border_size", _FALLBACK_THUMB_BORDER)

        # Marks: position -> label text
        self._marks: dict[float, str] = {}

        # Tooltip
        self._tooltip_enabled: bool = False
        self._tooltip_label: QLabel | None = None

        # Drag state
        self._dragging: int = -1  # -1=none, 0=low thumb, 1=high thumb
        self._hover_thumb: int = -1  # which thumb is hovered

        # Animated thumb position (for programmatic changes)
        self._anim = QPropertyAnimation(self, b"thumbPos", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._anim_high = QPropertyAnimation(self, b"thumbPosHigh", self)
        self._anim_high.setDuration(150)
        self._anim_high.setEasingCurve(QEasingCurve.Type.InOutCubic)

    # -- Animated properties --

    def _get_thumb_pos(self) -> float:
        return self._thumb_pos

    def _set_thumb_pos(self, v: float) -> None:
        self._thumb_pos = v
        self.update()

    thumbPos = Property(float, _get_thumb_pos, _set_thumb_pos)  # type: ignore[assignment]

    def _get_thumb_pos_high(self) -> float:
        return self._thumb_pos_high

    def _set_thumb_pos_high(self, v: float) -> None:
        self._thumb_pos_high = v
        self.update()

    thumbPosHigh = Property(float, _get_thumb_pos_high, _set_thumb_pos_high)  # type: ignore[assignment]

    # -- Geometry helpers --

    def _track_length(self) -> int:
        """Usable track length in pixels (excluding thumb radius margins)."""
        total = self.height() if self._vertical else self.width()
        return max(1, total - self._thumb_d)

    def _frac_to_px(self, frac: float) -> float:
        """Convert a normalised [0,1] fraction to pixel offset along the track.

        Accounts for reverse mode: when reverse is True, the direction is
        flipped (horizontal: right-to-left, vertical: top-to-bottom).
        """
        margin = self._thumb_d / 2.0
        effective_frac = (1.0 - frac) if self._reverse else frac
        if self._vertical:
            # Vertical: normally 0 at bottom, 1 at top
            return margin + (1.0 - effective_frac) * self._track_length()
        return margin + effective_frac * self._track_length()

    def _px_to_frac(self, px: float) -> float:
        """Convert a pixel offset to normalised [0,1] fraction.

        Accounts for reverse mode.
        """
        margin = self._thumb_d / 2.0
        length = self._track_length()
        if self._vertical:
            raw = max(0.0, min(1.0, 1.0 - (px - margin) / length))
        else:
            raw = max(0.0, min(1.0, (px - margin) / length))
        return (1.0 - raw) if self._reverse else raw

    def _frac_to_value(self, frac: float) -> float:
        """Convert normalised fraction to actual value.

        In mark-snap mode, snaps to the nearest mark position instead of step.
        """
        raw = self._min + frac * (self._max - self._min)
        if self._mark_snap and self._marks:
            return self._snap_to_nearest_mark(raw)
        return _snap_to_step(raw, self._min, self._max, self._step)

    def _snap_to_nearest_mark(self, value: float) -> float:
        """Snap value to the nearest mark position."""
        if not self._marks:
            return value
        closest = min(self._marks.keys(), key=lambda m: abs(m - value))
        return closest

    def _value_to_frac(self, value: float) -> float:
        """Convert actual value to normalised fraction."""
        span = self._max - self._min
        if span == 0:
            return 0.0
        return max(0.0, min(1.0, (value - self._min) / span))

    def _thumb_center(self, frac: float) -> QPoint:
        """Return the center point of a thumb at the given fraction."""
        px = self._frac_to_px(frac)
        if self._vertical:
            return QPoint(self.width() // 2, int(px))
        return QPoint(int(px), self.height() // 2)

    def _hit_thumb(self, pos: QPoint) -> int:
        """Return which thumb (0, 1, or -1) is under the given point."""
        r = self._thumb_d / 2.0 + 4  # extra hit area
        if self._range_mode:
            c_high = self._thumb_center(self._thumb_pos_high)
            if (pos - c_high).manhattanLength() <= r * 1.5:
                return 1
            c_low = self._thumb_center(self._thumb_pos)
            if (pos - c_low).manhattanLength() <= r * 1.5:
                return 0
        else:
            c = self._thumb_center(self._thumb_pos)
            if (pos - c).manhattanLength() <= r * 1.5:
                return 0
        return -1

    # -- Public setters --

    def set_value_frac(self, frac: float, animate: bool = True) -> None:
        """Set the low thumb position as a fraction, optionally animated."""
        frac = max(0.0, min(1.0, frac))
        if self._range_mode:
            frac = min(frac, self._thumb_pos_high)
        if animate:
            self._anim.stop()
            self._anim.setStartValue(self._thumb_pos)
            self._anim.setEndValue(frac)
            self._anim.start()
        else:
            self._thumb_pos = frac
            self.update()

    def set_value_high_frac(self, frac: float, animate: bool = True) -> None:
        """Set the high thumb position as a fraction, optionally animated."""
        frac = max(0.0, min(1.0, frac))
        if self._range_mode:
            frac = max(frac, self._thumb_pos)
        if animate:
            self._anim_high.stop()
            self._anim_high.setStartValue(self._thumb_pos_high)
            self._anim_high.setEndValue(frac)
            self._anim_high.start()
        else:
            self._thumb_pos_high = frac
            self.update()

    def update_dims(self) -> None:
        """Refresh track/thumb dimensions from tokens."""
        dims = _get_slider_dims()
        self._track_h = dims.get("track_height", _FALLBACK_TRACK_HEIGHT)
        self._thumb_d = dims.get("thumb_size", _FALLBACK_THUMB_SIZE)
        self._thumb_border = dims.get("thumb_border_size", _FALLBACK_THUMB_BORDER)
        self.update()

    # -- Painting --

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the track, filled region, marks, and thumbs."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        track_h = self._track_h
        thumb_d = self._thumb_d

        # Colors
        track_color = _get_color("colors", "rail_color", "#e0e0e6")
        fill_color = _get_color("colors", "primary", "#18a058")
        thumb_fill = _get_color("colors", "white", "#ffffff")
        thumb_border_color = fill_color
        disabled_fill = _get_color("colors", "text_disabled", "#c2c2c2")

        if self._disabled:
            fill_color = disabled_fill
            thumb_border_color = disabled_fill

        # -- Draw track background --
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        if self._vertical:
            tx = (w - track_h) / 2.0
            painter.drawRoundedRect(
                QRectF(tx, thumb_d / 2.0, track_h, h - thumb_d),
                track_h / 2.0, track_h / 2.0,
            )
        else:
            ty = (h - track_h) / 2.0
            painter.drawRoundedRect(
                QRectF(thumb_d / 2.0, ty, w - thumb_d, track_h),
                track_h / 2.0, track_h / 2.0,
            )

        # -- Draw filled region --
        painter.setBrush(fill_color)
        if self._range_mode:
            lo_px = self._frac_to_px(self._thumb_pos)
            hi_px = self._frac_to_px(self._thumb_pos_high)
            if self._vertical:
                tx = (w - track_h) / 2.0
                top = min(lo_px, hi_px)
                bot = max(lo_px, hi_px)
                painter.drawRoundedRect(
                    QRectF(tx, top, track_h, bot - top),
                    track_h / 2.0, track_h / 2.0,
                )
            else:
                left = min(lo_px, hi_px)
                right = max(lo_px, hi_px)
                ty = (h - track_h) / 2.0
                painter.drawRoundedRect(
                    QRectF(left, ty, right - left, track_h),
                    track_h / 2.0, track_h / 2.0,
                )
        else:
            px = self._frac_to_px(self._thumb_pos)
            if self._vertical:
                tx = (w - track_h) / 2.0
                painter.drawRoundedRect(
                    QRectF(tx, px, track_h, h - thumb_d / 2.0 - px),
                    track_h / 2.0, track_h / 2.0,
                )
            else:
                ty = (h - track_h) / 2.0
                if self._reverse:
                    # Reverse: fill from thumb to right edge
                    painter.drawRoundedRect(
                        QRectF(px, ty, w - thumb_d / 2.0 - px, track_h),
                        track_h / 2.0, track_h / 2.0,
                    )
                else:
                    # Normal: fill from left edge to thumb
                    painter.drawRoundedRect(
                        QRectF(thumb_d / 2.0, ty, px - thumb_d / 2.0, track_h),
                        track_h / 2.0, track_h / 2.0,
                    )

        # -- Draw mark ticks --
        if self._marks:
            mark_color = _get_color("colors", "text_secondary", "#667085")
            tick_pen = QPen(mark_color)
            tick_pen.setWidthF(1.5)
            painter.setPen(tick_pen)
            for pos_val in self._marks:
                frac = self._value_to_frac(pos_val)
                px_pos = self._frac_to_px(frac)
                if self._vertical:
                    cx = w / 2.0
                    painter.drawLine(
                        int(cx - track_h), int(px_pos),
                        int(cx + track_h), int(px_pos),
                    )
                else:
                    cy = h / 2.0
                    painter.drawLine(
                        int(px_pos), int(cy - track_h),
                        int(px_pos), int(cy + track_h),
                    )

        # -- Draw thumbs --
        self._draw_thumb(
            painter, self._thumb_pos, thumb_d, thumb_fill, thumb_border_color,
            self._hover_thumb == 0 or self._dragging == 0,
        )
        if self._range_mode:
            self._draw_thumb(
                painter, self._thumb_pos_high, thumb_d, thumb_fill, thumb_border_color,
                self._hover_thumb == 1 or self._dragging == 1,
            )

        painter.end()

    def _draw_thumb(
        self, painter: QPainter, frac: float, d: int,
        fill: QColor, border_color: QColor, active: bool,
    ) -> None:
        """Draw a single thumb circle at the given fraction position."""
        center = self._thumb_center(frac)
        r = d / 2.0
        active_scale = 1.2 if active else 1.0
        draw_r = r * active_scale

        # Shadow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawEllipse(
            QRectF(center.x() - draw_r + 1, center.y() - draw_r + 1, draw_r * 2, draw_r * 2),
        )

        # Border + fill
        pen = QPen(border_color)
        pen.setWidthF(self._thumb_border)
        painter.setPen(pen)
        painter.setBrush(fill)
        painter.drawEllipse(
            QRectF(center.x() - draw_r, center.y() - draw_r, draw_r * 2, draw_r * 2),
        )

    # -- Mouse events --

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging a thumb or jump to click position."""
        if self._disabled or event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)

        hit = self._hit_thumb(event.pos())
        if hit >= 0:
            self._dragging = hit
            self.drag_started.emit()
        else:
            # Click on track: move nearest thumb
            coord = event.pos().y() if self._vertical else event.pos().x()
            frac = self._px_to_frac(coord)
            snapped_val = self._frac_to_value(frac)
            snapped_frac = self._value_to_frac(snapped_val)

            if self._range_mode:
                dist_lo = abs(snapped_frac - self._thumb_pos)
                dist_hi = abs(snapped_frac - self._thumb_pos_high)
                if dist_lo <= dist_hi:
                    self._dragging = 0
                    self._thumb_pos = snapped_frac
                else:
                    self._dragging = 1
                    self._thumb_pos_high = snapped_frac
                self._enforce_range_order()
            else:
                self._dragging = 0
                self._thumb_pos = snapped_frac
            self.drag_started.emit()
            self.update()
            self.thumb_moved.emit()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update thumb position while dragging, or update hover state."""
        if self._disabled:
            return super().mouseMoveEvent(event)

        if self._dragging >= 0:
            coord = event.pos().y() if self._vertical else event.pos().x()
            frac = self._px_to_frac(coord)
            snapped_val = self._frac_to_value(frac)
            snapped_frac = self._value_to_frac(snapped_val)

            if self._dragging == 0:
                self._thumb_pos = snapped_frac
            else:
                self._thumb_pos_high = snapped_frac
            self._enforce_range_order()
            self.update()
            self.thumb_moved.emit()
            self._update_tooltip(event.globalPosition().toPoint())
        else:
            # Hover detection
            old_hover = self._hover_thumb
            self._hover_thumb = self._hit_thumb(event.pos())
            if old_hover != self._hover_thumb:
                self.update()
                if self._hover_thumb >= 0:
                    self.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """End thumb dragging."""
        if self._dragging >= 0:
            self._dragging = -1
            self._hide_tooltip()
            self.update()
            self.drag_ended.emit()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event: Any) -> None:  # noqa: N802
        """Clear hover state when mouse leaves."""
        self._hover_thumb = -1
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().leaveEvent(event)

    # -- Range enforcement --

    def _enforce_range_order(self) -> None:
        """Ensure low <= high in range mode by swapping if needed."""
        if self._range_mode and self._thumb_pos > self._thumb_pos_high:
            self._thumb_pos, self._thumb_pos_high = self._thumb_pos_high, self._thumb_pos
            # Swap drag target too
            if self._dragging == 0:
                self._dragging = 1
            elif self._dragging == 1:
                self._dragging = 0

    # -- Tooltip --

    def _update_tooltip(self, global_pos: QPoint) -> None:
        """Show or update the tooltip at the configured placement relative to the active thumb."""
        if not self._tooltip_enabled:
            return
        if self._tooltip_label is None:
            self._tooltip_label = QLabel(self.window())
            self._tooltip_label.setObjectName("slider_tooltip")
            self._tooltip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._apply_tooltip_style()
        frac = self._thumb_pos if self._dragging == 0 else self._thumb_pos_high
        val = self._frac_to_value(frac)
        display = str(int(val)) if val == int(val) else f"{val:.2f}"
        self._tooltip_label.setText(display)
        self._tooltip_label.adjustSize()

        # Position relative to the thumb center based on placement
        thumb_center = self._thumb_center(frac)
        tw = self._tooltip_label.width()
        th = self._tooltip_label.height()
        gap = 8

        placement = getattr(self, "_tooltip_placement", "top")
        if placement == "bottom":
            tip_x = thumb_center.x() - tw // 2
            tip_y = thumb_center.y() + self._thumb_d // 2 + gap
        elif placement == "left":
            tip_x = thumb_center.x() - tw - self._thumb_d // 2 - gap
            tip_y = thumb_center.y() - th // 2
        elif placement == "right":
            tip_x = thumb_center.x() + self._thumb_d // 2 + gap
            tip_y = thumb_center.y() - th // 2
        else:  # "top" (default)
            tip_x = thumb_center.x() - tw // 2
            tip_y = thumb_center.y() - th - gap

        parent_pos = self.mapTo(self.window(), QPoint(tip_x, tip_y))
        self._tooltip_label.move(parent_pos)
        self._tooltip_label.show()
        self._tooltip_label.raise_()

    def _apply_tooltip_style(self) -> None:
        """Apply theme-aware inline style to the tooltip label."""
        if self._tooltip_label is None:
            return
        try:
            engine = ThemeEngine.instance()
            bg = str(engine.get_token("colors", "indicator_color"))
            fg = str(engine.get_token("colors", "white"))
            radius = str(engine.get_token("radius", "medium"))
            font_sz = str(engine.get_token("font_sizes", "medium"))
            self._tooltip_label.setStyleSheet(
                f"background-color: {bg}; color: {fg}; border: 1px solid {bg};"
                f" border-radius: {radius}px; padding: 4px 10px; font-size: {font_sz}px;"
            )
        except Exception:
            pass

    def _hide_tooltip(self) -> None:
        """Hide the tooltip label."""
        if self._tooltip_label is not None:
            self._tooltip_label.hide()


class TSlider(
    HoverEffectMixin,
    BaseWidget,
):
    """Slider component supporting single-thumb and dual-thumb (range) modes.

    Provides step snapping, marks/labels, tooltip display, vertical
    orientation, disabled state, reverse direction, keyboard control,
    tooltip placement, and mark-snap mode. Visual style follows NaiveUI
    conventions with custom-painted track and thumbs driven by Design Tokens.

    Args:
        value: Initial value. For range mode pass a (low, high) tuple.
        min_val: Minimum allowed value. Default 0.
        max_val: Maximum allowed value. Default 100.
        step: Step increment for snapping. Default 1. Pass ``"mark"`` to
            snap to the nearest mark position instead of a fixed step.
        range: Whether to enable dual-thumb range selection.
        marks: Dict mapping values to label strings for tick marks.
        tooltip: Whether to show a value tooltip while dragging.
        vertical: Whether to render the slider vertically.
        disabled: Whether the slider starts disabled.
        reverse: Whether to reverse the slider direction. When True,
            horizontal sliders increase right-to-left and vertical
            sliders increase top-to-bottom.
        keyboard: Whether keyboard arrow keys adjust the value. Default True.
        placement: Tooltip placement relative to the thumb
            (``"top"`` | ``"bottom"`` | ``"left"`` | ``"right"``). Default ``"top"``.
        parent: Optional parent widget.

    Signals:
        value_changed: Emitted with the current value whenever it changes.
            In single mode emits int|float; in range mode emits tuple.
        drag_start: Emitted when the user begins dragging a thumb.
        drag_end: Emitted when the user finishes dragging a thumb.

    Example:
        >>> slider = TSlider(value=30, min_val=0, max_val=100, step=5)
        >>> slider.value_changed.connect(lambda v: print(f"Value: {v}"))
        >>> slider = TSlider(value=(20, 80), range=True, marks={0: "0", 50: "50", 100: "100"})
        >>> slider = TSlider(value=50, reverse=True, keyboard=False)
    """

    value_changed = Signal(object)
    drag_start = Signal()
    drag_end = Signal()

    def __init__(
        self,
        value: SliderValue = 0,
        min_val: int | float = 0,
        max_val: int | float = 100,
        step: int | float | str = 1,
        range: bool = False,  # noqa: A002
        marks: dict[int | float, str] | None = None,
        tooltip: bool = False,
        vertical: bool = False,
        disabled: bool = False,
        reverse: bool = False,
        keyboard: bool = True,
        placement: str = "top",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._init_hover_effect()

        self._min = float(min_val)
        self._max = float(max_val)
        self._range_mode = range
        self._vertical = vertical
        self._disabled = disabled
        self._marks: dict[float, str] = {float(k): v for k, v in marks.items()} if marks else {}
        self._tooltip = tooltip
        self._reverse = reverse
        self._keyboard = keyboard
        self._placement = placement

        # Handle step: "mark" string means snap to marks
        self._mark_snap = isinstance(step, str) and step == "mark"
        self._step = 1.0 if self._mark_snap else float(step)
        self._step_raw: int | float | str = step  # preserve original for property access

        # Build UI
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._track = _SliderTrack(self)
        self._track._min = self._min
        self._track._max = self._max
        self._track._step = self._step
        self._track._range_mode = self._range_mode
        self._track._vertical = self._vertical
        self._track._disabled = self._disabled
        self._track._marks = self._marks
        self._track._tooltip_enabled = self._tooltip
        self._track._reverse = self._reverse
        self._track._mark_snap = self._mark_snap
        self._track._tooltip_placement = self._placement
        self._layout.addWidget(self._track)

        # Mark labels below the track
        self._mark_labels: list[QLabel] = []
        if self._marks and not self._vertical:
            self._build_mark_labels()

        # QSS dynamic properties
        self.setProperty("disabled", str(disabled).lower())
        self.setProperty("vertical", str(vertical).lower())
        self.setProperty("reverse", str(reverse).lower())

        # Set initial value
        self._set_initial_value(value)

        # Connect track thumb_moved to emit value_changed
        self._track.thumb_moved.connect(self._on_thumb_moved)
        # Connect track drag signals to public signals
        self._track.drag_started.connect(self.drag_start.emit)
        self._track.drag_ended.connect(self.drag_end.emit)

        # Enable keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if disabled:
            self.setEnabled(False)

        self.apply_theme()

    # -- Value access --

    @property
    def value(self) -> SliderValue:
        """Return the current slider value.

        Returns:
            Single number in normal mode, (low, high) tuple in range mode.
        """
        if self._range_mode:
            lo = self._track._frac_to_value(self._track._thumb_pos)
            hi = self._track._frac_to_value(self._track._thumb_pos_high)
            return (lo, hi)
        return self._track._frac_to_value(self._track._thumb_pos)

    def set_value(self, value: SliderValue) -> None:
        """Set the slider value programmatically.

        Args:
            value: Single number or (low, high) tuple for range mode.
        """
        if self._range_mode and isinstance(value, tuple):
            lo, hi = float(value[0]), float(value[1])
            lo = _snap_to_step(lo, self._min, self._max, self._step)
            hi = _snap_to_step(hi, self._min, self._max, self._step)
            if lo > hi:
                lo, hi = hi, lo
            self._track.set_value_frac(self._track._value_to_frac(lo), animate=False)
            self._track.set_value_high_frac(self._track._value_to_frac(hi), animate=False)
        else:
            v = float(value) if not isinstance(value, tuple) else float(value[0])
            v = _snap_to_step(v, self._min, self._max, self._step)
            self._track.set_value_frac(self._track._value_to_frac(v), animate=False)
        self.value_changed.emit(self.value)

    # -- Property accessors --

    @property
    def min_val(self) -> float:
        """Return the minimum value."""
        return self._min

    @property
    def max_val(self) -> float:
        """Return the maximum value."""
        return self._max

    @property
    def step(self) -> float | str:
        """Return the step size, or ``"mark"`` if mark-snap mode is active."""
        return self._step_raw

    @property
    def is_range(self) -> bool:
        """Return whether range mode is active."""
        return self._range_mode

    @property
    def is_vertical(self) -> bool:
        """Return whether vertical mode is active."""
        return self._vertical

    @property
    def marks(self) -> dict[float, str]:
        """Return the marks dictionary."""
        return dict(self._marks)

    @property
    def is_disabled(self) -> bool:
        """Return whether the slider is disabled."""
        return self._disabled

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable the slider.

        Args:
            disabled: True to disable interaction.
        """
        self._disabled = disabled
        self._track._disabled = disabled
        self.setEnabled(not disabled)
        self.setProperty("disabled", str(disabled).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self._track.update()

    def set_tooltip(self, enabled: bool) -> None:
        """Enable or disable the tooltip display while dragging.

        Args:
            enabled: True to show tooltip, False to hide.
        """
        self._tooltip = enabled
        self._track._tooltip_enabled = enabled

    def set_step(self, step: int | float | str) -> None:
        """Set the step increment for snapping.

        Args:
            step: New step value, or ``"mark"`` to snap to mark positions.
        """
        self._step_raw = step
        self._mark_snap = isinstance(step, str) and step == "mark"
        self._step = 1.0 if self._mark_snap else float(step)
        self._track._step = self._step
        self._track._mark_snap = self._mark_snap

    def set_marks(self, marks: dict[int | float, str]) -> None:
        """Update the marks dictionary and rebuild labels.

        Args:
            marks: Dict mapping values to label strings.
        """
        self._marks = {float(k): v for k, v in marks.items()}
        self._track._marks = self._marks
        # Rebuild mark labels
        for lbl in self._mark_labels:
            lbl.deleteLater()
        self._mark_labels.clear()
        if self._marks and not self._vertical:
            self._build_mark_labels()
        self._track.update()

    # -- New property accessors --

    @property
    def is_reverse(self) -> bool:
        """Return whether reverse mode is active."""
        return self._reverse

    @property
    def is_keyboard(self) -> bool:
        """Return whether keyboard control is enabled."""
        return self._keyboard

    @property
    def placement(self) -> str:
        """Return the tooltip placement."""
        return self._placement

    def set_reverse(self, reverse: bool) -> None:
        """Enable or disable reverse slider direction.

        Args:
            reverse: True to reverse the slider direction.
        """
        self._reverse = reverse
        self._track._reverse = reverse
        self.setProperty("reverse", str(reverse).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self._track.update()

    def set_keyboard(self, enabled: bool) -> None:
        """Enable or disable keyboard arrow key control.

        Args:
            enabled: True to allow keyboard control.
        """
        self._keyboard = enabled

    def set_placement(self, placement: str) -> None:
        """Set the tooltip placement relative to the thumb.

        Args:
            placement: One of ``"top"``, ``"bottom"``, ``"left"``, ``"right"``.
        """
        self._placement = placement
        self._track._tooltip_placement = placement

    # -- Keyboard events --

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle keyboard arrow keys to adjust slider value.

        Respects the ``keyboard`` property: when False, arrow key events
        are ignored and passed to the parent.
        """
        if self._disabled or not self._keyboard:
            return super().keyPressEvent(event)

        key = event.key()
        # Determine step delta
        if self._mark_snap and self._marks:
            delta_frac = self._get_mark_step_frac(key)
        else:
            span = self._max - self._min
            delta_frac = (self._step / span) if span > 0 else 0.0
            if key in (Qt.Key.Key_Left, Qt.Key.Key_Down):
                delta_frac = -delta_frac
            elif key not in (Qt.Key.Key_Right, Qt.Key.Key_Up):
                return super().keyPressEvent(event)

        # In reverse mode, invert the direction
        if self._reverse:
            delta_frac = -delta_frac

        new_frac = max(0.0, min(1.0, self._track._thumb_pos + delta_frac))
        snapped_val = self._track._frac_to_value(new_frac)
        snapped_frac = self._track._value_to_frac(snapped_val)
        self._track.set_value_frac(snapped_frac, animate=True)
        self._track.thumb_moved.emit()

    def _get_mark_step_frac(self, key: int) -> float:
        """Get the fraction delta to move to the next/previous mark position."""
        sorted_marks = sorted(self._marks.keys())
        if not sorted_marks:
            return 0.0
        current_val = self._track._frac_to_value(self._track._thumb_pos)
        if key in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            # Find next mark above current value
            for m in sorted_marks:
                if m > current_val + 1e-9:
                    target_frac = self._track._value_to_frac(m)
                    return target_frac - self._track._thumb_pos
            return 0.0
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            # Find previous mark below current value
            for m in reversed(sorted_marks):
                if m < current_val - 1e-9:
                    target_frac = self._track._value_to_frac(m)
                    return target_frac - self._track._thumb_pos
            return 0.0
        return 0.0

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this slider."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("slider.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass
        if hasattr(self, "_track"):
            self._track.update_dims()
            self._track.update()
            # Refresh tooltip style for theme color changes
            if self._track._tooltip_label is not None:
                self._track._apply_tooltip_style()

    # -- Size hints --

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size."""
        dims = _get_slider_dims()
        thumb = dims.get("thumb_size", _FALLBACK_THUMB_SIZE)
        marks_extra = 20 if self._marks else 0
        if self._vertical:
            return QSize(thumb + 24 + marks_extra, 200)
        return QSize(200, thumb + 24 + marks_extra)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Provide a minimum size."""
        dims = _get_slider_dims()
        thumb = dims.get("thumb_size", _FALLBACK_THUMB_SIZE)
        if self._vertical:
            return QSize(thumb + 16, 60)
        return QSize(60, thumb + 16)

    # -- Private helpers --

    def _set_initial_value(self, value: SliderValue) -> None:
        """Set the initial thumb positions without animation."""
        if self._range_mode and isinstance(value, tuple):
            lo, hi = float(value[0]), float(value[1])
            lo = _snap_to_step(lo, self._min, self._max, self._step)
            hi = _snap_to_step(hi, self._min, self._max, self._step)
            if lo > hi:
                lo, hi = hi, lo
            self._track.set_value_frac(self._track._value_to_frac(lo), animate=False)
            self._track.set_value_high_frac(self._track._value_to_frac(hi), animate=False)
        else:
            v = float(value) if not isinstance(value, tuple) else float(value[0])
            v = _snap_to_step(v, self._min, self._max, self._step)
            self._track.set_value_frac(self._track._value_to_frac(v), animate=False)

    def _on_thumb_moved(self) -> None:
        """Slot called when the track reports a thumb position change."""
        self.value_changed.emit(self.value)

    def _build_mark_labels(self) -> None:
        """Create QLabel widgets for each mark below the track (horizontal mode)."""
        for val, text in sorted(self._marks.items()):
            lbl = QLabel(text, self)
            lbl.setProperty("class", "slider-mark-label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.adjustSize()
            self._mark_labels.append(lbl)

    def resizeEvent(self, event: Any) -> None:  # noqa: N802
        """Reposition mark labels on resize."""
        super().resizeEvent(event)
        if not self._mark_labels or self._vertical:
            return
        sorted_marks = sorted(self._marks.items())
        track_top = self._track.y() + self._track.height()
        for i, (val, _text) in enumerate(sorted_marks):
            if i >= len(self._mark_labels):
                break
            lbl = self._mark_labels[i]
            frac = self._track._value_to_frac(val)
            px = self._track._frac_to_px(frac)
            lbl.move(int(self._track.x() + px - lbl.width() / 2), track_top + 2)
