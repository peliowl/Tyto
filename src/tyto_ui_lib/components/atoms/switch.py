"""TSwitch atom component: an iOS/NaiveUI-style toggle switch.

Provides a smooth sliding thumb animation with scale effect on toggle.
Supports size variants, loading state, square track mode, custom values,
rubber-band bounce effect, and track text display.
Emits ``toggled`` signal with the current boolean state on each change.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QSize,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color


# Default dimensions per size when tokens are unavailable
_FALLBACK_SIZES: dict[str, dict[str, int]] = {
    "small": {"width": 32, "height": 18, "thumb": 14},
    "medium": {"width": 44, "height": 22, "thumb": 18},
    "large": {"width": 56, "height": 26, "thumb": 22},
}


def _get_switch_dims(size_name: str) -> dict[str, int]:
    """Retrieve switch dimensions from ThemeEngine tokens or fallback."""
    try:
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens and tokens.switch_sizes and size_name in tokens.switch_sizes:
            return tokens.switch_sizes[size_name]
    except (RuntimeError, KeyError):
        pass
    return _FALLBACK_SIZES.get(size_name, _FALLBACK_SIZES["medium"])


class _SwitchTrack(QWidget):
    """Internal widget that paints the track and animated thumb.

    Supports round and square track modes, loading spinner on thumb,
    and text labels inside the track.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("switch_track")
        self.setFixedSize(QSize(44, 22))

        self._thumb_x: float = 2.0
        self._thumb_scale: float = 1.0
        self._checked = False
        self._round = True
        self._loading = False
        self._loading_angle = 0
        self._checked_text = ""
        self._unchecked_text = ""

        # Track/thumb dimensions (updated by resize_for_size)
        self._track_w = 44
        self._track_h = 22
        self._thumb_d = 18
        self._padding = 2

        # Loading spinner timer
        self._spin_timer = QTimer(self)
        self._spin_timer.setInterval(30)
        self._spin_timer.timeout.connect(self._advance_spinner)

        # Thumb position animation
        self._pos_anim = QPropertyAnimation(self, b"thumbX", self)
        self._pos_anim.setDuration(200)
        self._pos_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Thumb scale animation (brief enlarge then settle)
        self._scale_anim = QPropertyAnimation(self, b"thumbScale", self)
        self._scale_anim.setDuration(200)
        self._scale_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._anim_group = QParallelAnimationGroup(self)
        self._anim_group.addAnimation(self._pos_anim)
        self._anim_group.addAnimation(self._scale_anim)

        # Rubber-band enabled by default
        self._rubber_band = True

    # -- Animated properties --

    def _get_thumb_x(self) -> float:
        return self._thumb_x

    def _set_thumb_x(self, value: float) -> None:
        self._thumb_x = value
        self.update()

    thumbX = Property(float, _get_thumb_x, _set_thumb_x)  # type: ignore[assignment]

    def _get_thumb_scale(self) -> float:
        return self._thumb_scale

    def _set_thumb_scale(self, value: float) -> None:
        self._thumb_scale = value
        self.update()

    thumbScale = Property(float, _get_thumb_scale, _set_thumb_scale)  # type: ignore[assignment]

    def resize_for_size(self, dims: dict[str, int]) -> None:
        """Update track and thumb dimensions from token values.

        Args:
            dims: Dict with 'width', 'height', 'thumb' keys.
        """
        self._track_w = dims["width"]
        self._track_h = dims["height"]
        self._thumb_d = dims["thumb"]
        self._padding = (self._track_h - self._thumb_d) // 2
        self.setFixedSize(QSize(self._track_w, self._track_h))
        self._snap_thumb()

    def _snap_thumb(self) -> None:
        """Set thumb x to correct position without animation."""
        on_x = self._track_w - self._thumb_d - self._padding
        off_x = float(self._padding)
        self._thumb_x = on_x if self._checked else off_x
        self.update()

    def set_checked(self, checked: bool, animate: bool = True) -> None:
        """Update the visual state of the track.

        Args:
            checked: Whether the switch is on.
            animate: Whether to animate the transition.
        """
        self._checked = checked
        on_x = float(self._track_w - self._thumb_d - self._padding)
        off_x = float(self._padding)
        target_x = on_x if checked else off_x

        if animate:
            self._anim_group.stop()

            self._pos_anim.setStartValue(self._thumb_x)
            self._scale_anim.setStartValue(1.0)
            self._scale_anim.setEndValue(1.0)
            self._scale_anim.setKeyValueAt(0.5, 1.15)

            if self._rubber_band:
                overshoot = max(2.0, self._track_w * 0.06)
                overshoot_x = target_x + (overshoot if checked else -overshoot)
                overshoot_x = max(off_x, min(overshoot_x, on_x))
                self._pos_anim.setEndValue(overshoot_x)
                self._anim_group.start()
                # After main anim, bounce back to target (guard deleted C++ object)
                import weakref
                ref = weakref.ref(self)
                QTimer.singleShot(210, lambda: ref() is not None and ref()._bounce_to(target_x))
            else:
                self._pos_anim.setEndValue(target_x)
                self._anim_group.start()
        else:
            self._thumb_x = target_x
            self.update()

    def _bounce_to(self, target_x: float) -> None:
        """Animate a short bounce to the final target position."""
        try:
            bounce = QPropertyAnimation(self, b"thumbX", self)
            bounce.setDuration(120)
            bounce.setEasingCurve(QEasingCurve.Type.OutBounce)
            bounce.setStartValue(self._thumb_x)
            bounce.setEndValue(target_x)
            bounce.start()
        except RuntimeError:
            # C++ object already deleted (widget was garbage collected)
            pass

    def set_loading(self, loading: bool) -> None:
        """Enable or disable the loading spinner on the thumb."""
        self._loading = loading
        if loading:
            self._spin_timer.start()
        else:
            self._spin_timer.stop()
        self.update()

    def _advance_spinner(self) -> None:
        self._loading_angle = (self._loading_angle + 12) % 360
        self.update()

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the track, thumb, optional text, and optional loading spinner."""
        from PySide6.QtCore import QRectF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # -- Track color --
        engine = ThemeEngine.instance()
        if self._checked:
            try:
                track_color = parse_color(str(engine.get_token("colors", "primary")))
            except (RuntimeError, KeyError):
                track_color = QColor("#18a058")
        else:
            try:
                track_color = parse_color(str(engine.get_token("colors", "border")))
            except (RuntimeError, KeyError):
                track_color = QColor("#e0e0e6")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)

        if self._round:
            painter.drawRoundedRect(0, 0, w, h, h / 2.0, h / 2.0)
        else:
            radius = min(3.0, h / 6.0)
            painter.drawRoundedRect(0, 0, w, h, radius, radius)

        # -- Track text --
        text = self._checked_text if self._checked else self._unchecked_text
        if text:
            try:
                text_color = parse_color(str(engine.get_token("colors", "white")))
            except (RuntimeError, KeyError):
                text_color = QColor("#ffffff")
            painter.setPen(text_color)
            font = QFont()
            font.setPixelSize(max(9, self._thumb_d - 6))
            painter.setFont(font)

            thumb_space = self._thumb_d + self._padding * 2
            if self._checked:
                text_rect = QRectF(self._padding + 2, 0, w - thumb_space - 2, h)
            else:
                text_rect = QRectF(thumb_space, 0, w - thumb_space - 2, h)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

        # -- Thumb --
        painter.setPen(Qt.PenStyle.NoPen)
        thumb_radius = self._thumb_d / 2.0 * self._thumb_scale
        thumb_cy = h / 2.0
        thumb_offset = thumb_radius - self._thumb_d / 2.0

        # Subtle shadow
        shadow_color = QColor(0, 0, 0, 40)
        painter.setBrush(shadow_color)
        if self._round:
            painter.drawEllipse(
                self._thumb_x + 1 - thumb_offset,
                thumb_cy - thumb_radius + 1,
                thumb_radius * 2,
                thumb_radius * 2,
            )
        else:
            sq_r = min(2.0, thumb_radius / 3.0)
            painter.drawRoundedRect(
                int(self._thumb_x + 1 - thumb_offset),
                int(thumb_cy - thumb_radius + 1),
                int(thumb_radius * 2),
                int(thumb_radius * 2),
                sq_r, sq_r,
            )

        # White thumb
        painter.setBrush(QColor("#ffffff"))
        if self._round:
            painter.drawEllipse(
                self._thumb_x - thumb_offset,
                thumb_cy - thumb_radius,
                thumb_radius * 2,
                thumb_radius * 2,
            )
        else:
            sq_r = min(2.0, thumb_radius / 3.0)
            painter.drawRoundedRect(
                int(self._thumb_x - thumb_offset),
                int(thumb_cy - thumb_radius),
                int(thumb_radius * 2),
                int(thumb_radius * 2),
                sq_r, sq_r,
            )

        # -- Loading spinner on thumb --
        if self._loading:
            cx = self._thumb_x + self._thumb_d / 2.0 - thumb_offset
            cy_spin = thumb_cy
            spin_r = thumb_radius * 0.55
            pen = QPen(QColor(track_color))
            pen.setWidthF(max(1.5, spin_r / 3.0))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            arc_rect = QRectF(cx - spin_r, cy_spin - spin_r, spin_r * 2, spin_r * 2)
            painter.drawArc(arc_rect, self._loading_angle * 16, 270 * 16)

        painter.end()


class TSwitch(
    HoverEffectMixin,
    BaseWidget,
):
    """Toggle switch component in iOS/NaiveUI style.

    Provides a sliding thumb with scale animation on toggle. Supports
    size variants (small/medium/large), loading state, square track mode,
    custom checked/unchecked values, rubber-band bounce effect, and
    track text display.

    Args:
        checked: Initial on/off state.
        disabled: Whether the switch starts disabled.
        size: Size variant (small/medium/large). Default medium.
        loading: Whether to show a loading spinner and block interaction.
        round: Whether the track is fully rounded (True) or square (False).
        checked_value: Custom value returned by get_typed_value() when on.
        unchecked_value: Custom value returned by get_typed_value() when off.
        rubber_band: Whether to use rubber-band bounce animation on toggle.
        checked_text: Text displayed inside the track when on.
        unchecked_text: Text displayed inside the track when off.
        parent: Optional parent widget.

    Signals:
        toggled: Emitted with the current boolean state after each toggle.

    Example:
        >>> sw = TSwitch(size=TSwitch.SwitchSize.LARGE, checked_text="ON", unchecked_text="OFF")
        >>> sw.toggled.connect(lambda on: print(f"Switch is {'on' if on else 'off'}"))
    """

    class SwitchSize(str, Enum):
        """Available switch size variants."""

        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    toggled = Signal(bool)

    def __init__(
        self,
        checked: bool = False,
        disabled: bool = False,
        size: SwitchSize = SwitchSize.MEDIUM,
        loading: bool = False,
        round: bool = True,
        checked_value: Any = True,
        unchecked_value: Any = False,
        rubber_band: bool = True,
        checked_text: str = "",
        unchecked_text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._init_hover_effect()

        self._checked = checked
        self._disabled = disabled
        self._size = size
        self._loading = loading
        self._round = round
        self._checked_value = checked_value
        self._unchecked_value = unchecked_value
        self._rubber_band = rubber_band
        self._checked_text = checked_text
        self._unchecked_text = unchecked_text

        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._track = _SwitchTrack(self)
        self._layout.addWidget(self._track)

        # Apply size dimensions
        dims = _get_switch_dims(self._size.value)
        self._track.resize_for_size(dims)
        self._track._round = self._round
        self._track._rubber_band = self._rubber_band
        self._track._checked_text = self._checked_text
        self._track._unchecked_text = self._unchecked_text

        # QSS dynamic properties
        self.setProperty("checked", checked)
        self.setProperty("switchSize", self._size.value)
        self.setProperty("round", str(self._round).lower())
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Initial visual state
        if checked:
            self._track.set_checked(True, animate=False)

        if loading:
            self._track.set_loading(True)

        if disabled:
            self.setEnabled(False)

        self.apply_theme()

    # -- Public API --

    @property
    def size(self) -> SwitchSize:
        """Return the current size variant."""
        return self._size

    def set_size(self, size: SwitchSize) -> None:
        """Set the switch size variant.

        Args:
            size: New size variant.
        """
        if size == self._size:
            return
        self._size = size
        self.setProperty("switchSize", size.value)
        dims = _get_switch_dims(size.value)
        self._track.resize_for_size(dims)
        self.style().unpolish(self)
        self.style().polish(self)

    def is_checked(self) -> bool:
        """Return whether the switch is currently on."""
        return self._checked

    def set_checked(self, checked: bool) -> None:
        """Set the switch state programmatically.

        Args:
            checked: True for on, False for off.
        """
        if checked == self._checked:
            return
        self._checked = checked
        self._track.set_checked(checked)
        self.setProperty("checked", checked)
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled.emit(checked)

    def toggle(self) -> None:
        """Toggle the switch to the opposite state."""
        self.set_checked(not self._checked)

    def get_typed_value(self) -> Any:
        """Return checked_value or unchecked_value based on current state.

        Returns:
            checked_value if on, unchecked_value if off.
        """
        return self._checked_value if self._checked else self._unchecked_value

    def set_loading(self, loading: bool) -> None:
        """Enable or disable the loading state.

        When loading, the thumb shows a spinner and interaction is blocked.

        Args:
            loading: True to enable loading state.
        """
        self._loading = loading
        self._track.set_loading(loading)
        self.setProperty("loading", str(loading).lower())
        self.style().unpolish(self)
        self.style().polish(self)

    def set_round(self, round_mode: bool) -> None:
        """Set the track shape mode.

        Args:
            round_mode: True for fully rounded, False for square track.
        """
        self._round = round_mode
        self._track._round = round_mode
        self.setProperty("round", str(round_mode).lower())
        self._track.update()
        self.style().unpolish(self)
        self.style().polish(self)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this switch."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("switch.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass
        # Force the track to repaint so it picks up the new theme colors.
        if hasattr(self, "_track"):
            self._track.update()

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Toggle on left-click unless loading or disabled."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.isEnabled()
            and not self._loading
        ):
            self.toggle()
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size based on current size variant."""
        dims = _get_switch_dims(self._size.value)
        return QSize(dims["width"] + 8, dims["height"] + 8)
