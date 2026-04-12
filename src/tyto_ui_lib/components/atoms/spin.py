"""TSpin atom component: a loading spinner with standalone and nested modes.

Supports three animation types (ring, dots, pulse), three size variants,
optional description text, and a delay mechanism to avoid flicker on
short-lived loading states.

In nested mode the spinner overlays child content with a semi-transparent
mask (opacity 0.38).

Extended in V1.1.0:
- ``rotate``: control whether custom icon rotates (default True)
- ``content_class`` / ``content_style``: custom styling for nested content area
- ``stroke_width`` / ``stroke``: custom loading ring appearance
- ``set_icon()``: replace default animation with custom icon widget
- ``size`` accepts ``int`` for precise pixel control

Emits ``spinning_changed`` signal when the spinning state changes.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Union

from PySide6.QtCore import QRectF, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color

# Fallback animation element sizes when tokens are unavailable.
_FALLBACK_SPIN_SIZES: dict[str, int] = {
    "small": 20,
    "medium": 28,
    "large": 36,
}


def _get_spin_size(size_name: str) -> int:
    """Retrieve the animation element size from ThemeEngine tokens or fallback."""
    try:
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens and tokens.spin_sizes and size_name in tokens.spin_sizes:
            return int(tokens.spin_sizes[size_name].get("size", _FALLBACK_SPIN_SIZES.get(size_name, 28)))
    except (RuntimeError, KeyError):
        pass
    return _FALLBACK_SPIN_SIZES.get(size_name, 28)


class _SpinIndicator(QWidget):
    """Internal widget that paints the spinning animation.

    Supports ring, dots, and pulse animation types.
    Accepts custom stroke_width and stroke_color for ring rendering.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._animation_type = "ring"
        self._anim_size = 28
        self._angle = 0
        self._dot_phase = 0.0
        self._stroke_width: float = 2.0
        self._stroke_color: str | None = None  # None = use colors.primary

        self.setFixedSize(QSize(self._anim_size, self._anim_size))

        # Animation timer (~60fps)
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._advance)

    def set_animation_type(self, anim_type: str) -> None:
        """Set the animation type: 'ring', 'dots', or 'pulse'."""
        self._animation_type = anim_type
        self.update()

    def set_anim_size(self, size: int) -> None:
        """Update the animation element size."""
        self._anim_size = size
        self.setFixedSize(QSize(size, size))
        self.update()

    def set_stroke_width(self, width: float) -> None:
        """Set the ring stroke width."""
        self._stroke_width = width
        self.update()

    def set_stroke_color(self, color: str | None) -> None:
        """Set the ring stroke color. None restores theme default."""
        self._stroke_color = color
        self.update()

    def start(self) -> None:
        """Start the animation timer."""
        self._angle = 0
        self._dot_phase = 0.0
        self._timer.start()

    def stop(self) -> None:
        """Stop the animation timer."""
        self._timer.stop()

    def _advance(self) -> None:
        """Advance animation state by one frame."""
        self._angle = (self._angle + 6) % 360
        self._dot_phase += 0.08
        self.update()

    def _get_primary_color(self) -> QColor:
        """Get the ring color: custom stroke_color or theme primary."""
        if self._stroke_color is not None:
            c = parse_color(self._stroke_color)
            if c.isValid():
                return c
        try:
            engine = ThemeEngine.instance()
            return parse_color(str(engine.get_token("colors", "primary")))
        except (RuntimeError, KeyError):
            return QColor("#18a058")

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the animation based on the current type."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self._get_primary_color()
        s = self._anim_size

        if self._animation_type == "ring":
            self._paint_ring(painter, color, s)
        elif self._animation_type == "dots":
            self._paint_dots(painter, color, s)
        elif self._animation_type == "pulse":
            self._paint_pulse(painter, color, s)

        painter.end()

    def _paint_ring(self, painter: QPainter, color: QColor, s: int) -> None:
        """Paint a rotating arc ring using stroke_width."""
        pen = QPen(color)
        pen.setWidthF(max(self._stroke_width, 1.0))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        margin = pen.widthF() / 2.0 + 1
        rect = QRectF(margin, margin, s - margin * 2, s - margin * 2)
        painter.drawArc(rect, self._angle * 16, 270 * 16)

    def _paint_dots(self, painter: QPainter, color: QColor, s: int) -> None:
        """Paint three bouncing dots."""
        painter.setPen(Qt.PenStyle.NoPen)
        dot_r = max(2.0, s / 8.0)
        spacing = s / 4.0
        cy = s / 2.0

        for i in range(3):
            phase = self._dot_phase - i * 0.5
            bounce = abs(math.sin(phase)) * (s / 5.0)
            alpha = int(120 + 135 * abs(math.sin(phase)))
            c = QColor(color)
            c.setAlpha(min(255, alpha))
            painter.setBrush(c)
            cx = spacing + i * spacing
            painter.drawEllipse(QRectF(cx - dot_r, cy - bounce - dot_r, dot_r * 2, dot_r * 2))

    def _paint_pulse(self, painter: QPainter, color: QColor, s: int) -> None:
        """Paint a pulsing circle that fades in and out."""
        phase = (self._angle % 360) / 360.0
        scale = 0.4 + 0.6 * abs(math.sin(phase * math.pi))
        alpha = int(255 * (1.0 - 0.6 * abs(math.sin(phase * math.pi))))

        c = QColor(color)
        c.setAlpha(max(40, alpha))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c)

        r = s / 2.0 * scale
        cx = s / 2.0
        cy = s / 2.0
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))



class TSpin(BaseWidget):
    """Loading spinner with standalone and nested (overlay) modes.

    Supports three animation types: ring, dots, pulse.
    In nested mode, overlays child content with a semi-transparent mask.

    Args:
        spinning: Whether the spinner is active. Defaults to True.
        mode: Display mode — standalone or nested. Defaults to STANDALONE.
        animation_type: Animation style — ring, dots, or pulse. Defaults to RING.
        size: Animation element size variant or exact pixel size (int).
            Defaults to MEDIUM.
        description: Optional text displayed below the animation.
        delay: Milliseconds to wait before showing the spinner (0 = immediate).
        rotate: Whether custom icon rotates. Defaults to True.
        content_class: CSS class name for nested content area.
        content_style: Inline style dict for nested content area.
        stroke_width: Loading ring line width. Defaults to 2.
        stroke: Loading ring color string. None uses ``colors.primary``.
        parent: Optional parent widget.

    Signals:
        spinning_changed: Emitted with the new boolean spinning state.

    Example:
        >>> spin = TSpin(spinning=True, mode=TSpin.SpinMode.STANDALONE)
        >>> spin.set_spinning(False)
        >>> spin = TSpin(size=48, stroke_width=4, stroke="#ff0000")
    """

    class SpinMode(str, Enum):
        """Display mode for the spinner."""

        STANDALONE = "standalone"
        NESTED = "nested"

    class AnimationType(str, Enum):
        """Built-in animation styles."""

        RING = "ring"
        DOTS = "dots"
        PULSE = "pulse"

    class SpinSize(str, Enum):
        """Size variants for the animation element."""

        SMALL = "small"    # 20px
        MEDIUM = "medium"  # 28px
        LARGE = "large"    # 36px

    spinning_changed = Signal(bool)

    def __init__(
        self,
        spinning: bool = True,
        mode: SpinMode = SpinMode.STANDALONE,
        animation_type: AnimationType = AnimationType.RING,
        size: Union[SpinSize, int] = SpinSize.MEDIUM,
        description: str = "",
        delay: int = 0,
        rotate: bool = True,
        content_class: str = "",
        content_style: dict[str, str] | None = None,
        stroke_width: int | float = 2,
        stroke: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._spinning = False  # Will be set via set_spinning below
        self._mode = mode
        self._animation_type = animation_type
        self._description = description
        self._delay = max(0, delay)
        self._delay_active = False  # True while waiting for delay timer
        self._rotate = rotate
        self._content_class = content_class
        self._content_style = content_style or {}
        self._stroke_width = float(stroke_width) if stroke_width >= 0 else 2.0
        self._stroke: str | None = stroke
        self._custom_icon: QWidget | None = None
        self._custom_icon_container: QWidget | None = None

        # Resolve size: int or SpinSize enum
        if isinstance(size, int):
            if size <= 0:
                self._size = self.SpinSize.MEDIUM
                self._numeric_size: int | None = None
            else:
                self._size = self.SpinSize.MEDIUM  # fallback enum
                self._numeric_size = size
        else:
            self._size = size
            self._numeric_size = None

        # QSS dynamic properties
        self.setProperty("spinMode", self._mode.value)
        self.setProperty("spinSize", self._size.value if self._numeric_size is None else str(self._numeric_size))
        self.setProperty("animationType", self._animation_type.value)

        # Delay timer
        self._delay_timer = QTimer(self)
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._on_delay_elapsed)

        # Icon rotation timer
        self._icon_rotation_angle = 0
        self._icon_rotation_timer = QTimer(self)
        self._icon_rotation_timer.setInterval(16)
        self._icon_rotation_timer.timeout.connect(self._advance_icon_rotation)

        # Build the UI
        self._build_ui()

        # Apply theme and set initial state
        self.apply_theme()

        if spinning:
            self.set_spinning(True)

    def _resolve_anim_size(self) -> int:
        """Return the animation element pixel size."""
        if self._numeric_size is not None:
            return self._numeric_size
        return _get_spin_size(self._size.value)

    def _build_ui(self) -> None:
        """Construct the internal widget hierarchy."""
        anim_size = self._resolve_anim_size()

        if self._mode == self.SpinMode.STANDALONE:
            self._build_standalone(anim_size)
        else:
            self._build_nested(anim_size)

    def _build_standalone(self, anim_size: int) -> None:
        """Build standalone mode layout: centered spinner + optional description."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spinner indicator
        self._indicator = _SpinIndicator(self)
        self._indicator.set_anim_size(anim_size)
        self._indicator.set_animation_type(self._animation_type.value)
        self._indicator.set_stroke_width(self._stroke_width)
        self._indicator.set_stroke_color(self._stroke)
        layout.addWidget(self._indicator, 0, Qt.AlignmentFlag.AlignCenter)

        # Description label
        self._desc_label = QLabel(self)
        self._desc_label.setObjectName("spin_description")
        self._desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._desc_label.setText(self._description)
        self._desc_label.setVisible(bool(self._description))
        layout.addWidget(self._desc_label, 0, Qt.AlignmentFlag.AlignCenter)

        # No overlay or content in standalone mode
        self._overlay: QWidget | None = None
        self._content_widget: QWidget | None = None
        self._stacked: QStackedLayout | None = None

    def _build_nested(self, anim_size: int) -> None:
        """Build nested mode layout: stacked content + overlay with spinner."""
        self._stacked = QStackedLayout(self)
        self._stacked.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # Content container (child widgets go here)
        self._content_widget = QWidget(self)
        self._content_widget.setObjectName("spin_content")
        self._content_layout = QHBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        # Apply content_class and content_style
        self._apply_content_styling()
        self._stacked.addWidget(self._content_widget)

        # Overlay with spinner
        self._overlay = QWidget(self)
        self._overlay.setObjectName("spin_overlay")
        self._overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        overlay_layout = QVBoxLayout(self._overlay)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._indicator = _SpinIndicator(self._overlay)
        self._indicator.set_anim_size(anim_size)
        self._indicator.set_animation_type(self._animation_type.value)
        self._indicator.set_stroke_width(self._stroke_width)
        self._indicator.set_stroke_color(self._stroke)
        overlay_layout.addWidget(self._indicator, 0, Qt.AlignmentFlag.AlignCenter)

        self._desc_label = QLabel(self._overlay)
        self._desc_label.setObjectName("spin_description")
        self._desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._desc_label.setText(self._description)
        self._desc_label.setVisible(bool(self._description))
        overlay_layout.addWidget(self._desc_label, 0, Qt.AlignmentFlag.AlignCenter)

        self._stacked.addWidget(self._overlay)

        # Initially hidden
        self._overlay.setVisible(False)

    def _apply_content_styling(self) -> None:
        """Apply content_class and content_style to the nested content widget."""
        if self._content_widget is None:
            return
        if self._content_class:
            self._content_widget.setProperty("class", self._content_class)
        if self._content_style:
            parts = [f"{k}: {v}" for k, v in self._content_style.items()]
            self._content_widget.setStyleSheet(
                f"QWidget#spin_content {{ {'; '.join(parts)} }}"
            )

    # -- Public API --

    def set_spinning(self, spinning: bool) -> None:
        """Set the spinning state.

        When delay > 0 and spinning is set to True, the visual spinner
        appears only after the delay elapses. If spinning is set back to
        False before the delay, the spinner never appears.

        Args:
            spinning: Whether the spinner should be active.
        """
        if spinning == self._spinning:
            return

        self._spinning = spinning

        if spinning:
            if self._delay > 0:
                self._delay_active = True
                self._delay_timer.start(self._delay)
            else:
                self._show_spinner()
        else:
            self._delay_timer.stop()
            self._delay_active = False
            self._hide_spinner()

        self.spinning_changed.emit(spinning)

    def is_spinning(self) -> bool:
        """Return the current spinning state.

        Returns:
            True if the spinner is logically active (even if delayed).
        """
        return self._spinning

    def set_content(self, widget: QWidget) -> None:
        """Set child content for nested mode.

        In standalone mode this is a no-op.

        Args:
            widget: The widget to display beneath the overlay.
        """
        if self._mode != self.SpinMode.NESTED or self._content_widget is None:
            return
        # Clear existing content
        layout = self._content_widget.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item and item.widget():
                    item.widget().setParent(None)
            layout.addWidget(widget)

    def set_icon(self, widget: QWidget | None) -> None:
        """Set a custom icon widget, replacing the default animation.

        When a custom icon is set, the default _SpinIndicator is hidden
        and the custom widget is shown in its place. The ``rotate``
        property controls whether the icon rotates.

        Pass None to restore the default animation.

        Args:
            widget: Custom icon widget, or None to restore default.
        """
        # Remove previous custom icon
        if self._custom_icon is not None:
            self._custom_icon.setParent(None)
            self._custom_icon = None
        if self._custom_icon_container is not None:
            self._custom_icon_container.setParent(None)
            self._custom_icon_container = None
        self._icon_rotation_timer.stop()

        if widget is None:
            # Restore default indicator
            self._indicator.setVisible(True)
            if self._spinning:
                self._indicator.start()
            return

        self._custom_icon = widget
        self._indicator.setVisible(False)
        self._indicator.stop()

        # Wrap in a container for layout placement
        container = QWidget(self._indicator.parentWidget() or self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(widget)
        self._custom_icon_container = container

        # Insert into the layout where the indicator lives
        parent_widget = self._indicator.parentWidget()
        if parent_widget is not None:
            parent_layout = parent_widget.layout()
            if parent_layout is not None:
                parent_layout.addWidget(container)

        # Start rotation if needed
        if self._rotate and self._spinning:
            self._icon_rotation_timer.start()

    @property
    def rotate(self) -> bool:
        """Return whether custom icon rotates."""
        return self._rotate

    def set_rotate(self, rotate: bool) -> None:
        """Control whether custom icon rotates.

        Args:
            rotate: True to enable rotation animation for custom icon.
        """
        self._rotate = rotate
        if self._custom_icon is not None:
            if rotate and self._spinning:
                self._icon_rotation_timer.start()
            else:
                self._icon_rotation_timer.stop()

    @property
    def content_class(self) -> str:
        """Return the content area CSS class name."""
        return self._content_class

    def set_content_class(self, class_name: str) -> None:
        """Set CSS class for nested content area.

        Args:
            class_name: CSS class name string.
        """
        self._content_class = class_name
        self._apply_content_styling()

    @property
    def content_style(self) -> dict[str, str]:
        """Return the content area inline style dict."""
        return dict(self._content_style)

    def set_content_style(self, style: dict[str, str] | None) -> None:
        """Set inline style dict for nested content area.

        Args:
            style: Dict of CSS property-value pairs, or None to clear.
        """
        self._content_style = style or {}
        self._apply_content_styling()

    @property
    def stroke_width(self) -> float:
        """Return the loading ring stroke width."""
        return self._stroke_width

    def set_stroke_width(self, width: int | float) -> None:
        """Set loading ring stroke width.

        Args:
            width: Stroke width in pixels. Negative values fall back to 2.
        """
        self._stroke_width = float(width) if width >= 0 else 2.0
        if hasattr(self, "_indicator"):
            self._indicator.set_stroke_width(self._stroke_width)

    @property
    def stroke(self) -> str | None:
        """Return the loading ring color string."""
        return self._stroke

    def set_stroke(self, color: str | None) -> None:
        """Set loading ring color. None restores default.

        Args:
            color: Color string (hex, named, etc.) or None.
        """
        self._stroke = color
        if hasattr(self, "_indicator"):
            self._indicator.set_stroke_color(color)

    @property
    def mode(self) -> SpinMode:
        """Return the current display mode."""
        return self._mode

    @property
    def animation_type(self) -> AnimationType:
        """Return the current animation type."""
        return self._animation_type

    @property
    def size(self) -> SpinSize | int:
        """Return the current size variant or numeric size."""
        if self._numeric_size is not None:
            return self._numeric_size
        return self._size

    @property
    def description(self) -> str:
        """Return the current description text."""
        return self._description

    def set_description(self, text: str) -> None:
        """Set the description text below the animation.

        Args:
            text: New description text. Empty string hides the label.
        """
        self._description = text
        if hasattr(self, "_desc_label"):
            self._desc_label.setText(text)
            self._desc_label.setVisible(bool(text))

    def set_size(self, size: SpinSize | int) -> None:
        """Set the size variant and update the animation element size.

        Accepts a SpinSize enum or an int for precise pixel control.
        Negative int values fall back to SpinSize.MEDIUM.

        Args:
            size: New size variant or pixel size.
        """
        if isinstance(size, int):
            if size <= 0:
                self._size = self.SpinSize.MEDIUM
                self._numeric_size = None
            else:
                self._numeric_size = size
        else:
            self._size = size
            self._numeric_size = None

        size_label = self._size.value if self._numeric_size is None else str(self._numeric_size)
        self.setProperty("spinSize", size_label)
        anim_size = self._resolve_anim_size()
        if hasattr(self, "_indicator"):
            self._indicator.set_anim_size(anim_size)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_animation_type(self, anim_type: AnimationType) -> None:
        """Set the animation type and update the indicator.

        Args:
            anim_type: New animation type.
        """
        self._animation_type = anim_type
        self.setProperty("animationType", anim_type.value)
        if hasattr(self, "_indicator"):
            self._indicator.set_animation_type(anim_type.value)

    @property
    def delay(self) -> int:
        """Return the delay in milliseconds."""
        return self._delay

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this spin component."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("spin.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass
        # Force indicator repaint to pick up new theme colors
        if hasattr(self, "_indicator"):
            self._indicator.update()

    # -- Private helpers --

    def _on_delay_elapsed(self) -> None:
        """Called when the delay timer fires."""
        self._delay_active = False
        if self._spinning:
            self._show_spinner()

    def _show_spinner(self) -> None:
        """Make the spinner animation visible."""
        if self._custom_icon is not None:
            # Show custom icon instead of default indicator
            if self._custom_icon_container is not None:
                self._custom_icon_container.setVisible(True)
            if self._rotate:
                self._icon_rotation_timer.start()
        else:
            self._indicator.start()
            self._indicator.setVisible(True)
        if self._overlay is not None:
            self._overlay.setVisible(True)
            self._overlay.raise_()

    def _hide_spinner(self) -> None:
        """Hide the spinner animation."""
        self._indicator.stop()
        self._icon_rotation_timer.stop()
        if self._custom_icon_container is not None:
            self._custom_icon_container.setVisible(False)
        if self._mode == self.SpinMode.STANDALONE:
            self._indicator.setVisible(False)
        if self._overlay is not None:
            self._overlay.setVisible(False)

    def _advance_icon_rotation(self) -> None:
        """Advance the custom icon rotation by one frame."""
        if self._custom_icon is None:
            return
        self._icon_rotation_angle = (self._icon_rotation_angle + 6) % 360
        if self._custom_icon_container is not None:
            self._custom_icon_container.update()

    def cleanup(self) -> None:
        """Stop timers and disconnect signals before destruction."""
        self._delay_timer.stop()
        self._indicator.stop()
        self._icon_rotation_timer.stop()
        super().cleanup()
