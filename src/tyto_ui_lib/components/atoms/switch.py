"""TSwitch atom component: an iOS/NaiveUI-style toggle switch.

Provides a smooth sliding thumb animation with scale effect on toggle.
Emits ``toggled`` signal with the current boolean state on each change.
"""

from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QMouseEvent, QPainter
from PySide6.QtWidgets import QHBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


class _SwitchTrack(QWidget):
    """Internal widget that paints the track and animated thumb."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("switch_track")
        self.setFixedSize(QSize(40, 20))

        self._thumb_x: float = 3.0
        self._thumb_scale: float = 1.0
        self._checked = False

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

    def set_checked(self, checked: bool, animate: bool = True) -> None:
        """Update the visual state of the track.

        Args:
            checked: Whether the switch is on.
            animate: Whether to animate the transition.
        """
        self._checked = checked
        on_x = self.width() - 14 - 3  # thumb_diameter(14) + padding(3)
        off_x = 3.0
        target_x = on_x if checked else off_x

        if animate:
            self._anim_group.stop()
            self._pos_anim.setStartValue(self._thumb_x)
            self._pos_anim.setEndValue(target_x)
            self._scale_anim.setStartValue(1.0)
            self._scale_anim.setEndValue(1.0)
            # Insert a brief scale-up keyframe effect via sequential values
            self._scale_anim.setKeyValueAt(0.5, 1.15)
            self._anim_group.start()
        else:
            self._thumb_x = target_x
            self.update()

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the rounded track and circular thumb."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Draw track (rounded rectangle)
        engine = ThemeEngine.instance()
        if self._checked:
            try:
                track_color = QColor(str(engine.get_token("colors", "primary")))
            except (RuntimeError, KeyError):
                track_color = QColor("#18a058")
        else:
            try:
                track_color = QColor(str(engine.get_token("colors", "border")))
            except (RuntimeError, KeyError):
                track_color = QColor("#e0e0e6")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 0, w, h, h / 2.0, h / 2.0)

        # Draw thumb (white circle with shadow)
        thumb_diameter = 14.0
        thumb_radius = thumb_diameter / 2.0 * self._thumb_scale
        thumb_cy = h / 2.0

        # Subtle shadow
        shadow_color = QColor(0, 0, 0, 40)
        painter.setBrush(shadow_color)
        painter.drawEllipse(
            self._thumb_x + 1 - (thumb_radius - thumb_diameter / 2.0),
            thumb_cy - thumb_radius + 1,
            thumb_radius * 2,
            thumb_radius * 2,
        )

        # White thumb
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(
            self._thumb_x - (thumb_radius - thumb_diameter / 2.0),
            thumb_cy - thumb_radius,
            thumb_radius * 2,
            thumb_radius * 2,
        )

        painter.end()


class TSwitch(
    HoverEffectMixin,
    BaseWidget,
):
    """Toggle switch component in iOS/NaiveUI style.

    Provides a sliding thumb with scale animation on toggle. Emits
    ``toggled`` with the current boolean state whenever the switch
    is clicked or toggled programmatically.

    Args:
        checked: Initial on/off state.
        disabled: Whether the switch starts disabled.
        parent: Optional parent widget.

    Signals:
        toggled: Emitted with the current boolean state after each toggle.

    Example:
        >>> sw = TSwitch(checked=False)
        >>> sw.toggled.connect(lambda on: print(f"Switch is {'on' if on else 'off'}"))
    """

    toggled = Signal(bool)

    def __init__(
        self,
        checked: bool = False,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Initialise mixin resources
        self._init_hover_effect()

        self._checked = checked
        self._disabled = disabled

        # Layout: [track]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._track = _SwitchTrack(self)
        self._layout.addWidget(self._track)

        # Dynamic property for QSS
        self.setProperty("checked", checked)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply initial state without animation
        if checked:
            self._track.set_checked(True, animate=False)

        if disabled:
            self.setEnabled(False)

        self.apply_theme()

    # -- Public API --

    def is_checked(self) -> bool:
        """Return whether the switch is currently on.

        Returns:
            True if the switch is in the on state.
        """
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
        # Force the track to repaint so it picks up the new theme colors
        # (the track reads colors.border / colors.primary in paintEvent).
        # Guard: _track may not exist yet if called from BaseWidget.__init__.
        if hasattr(self, "_track"):
            self._track.update()

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Toggle on left-click."""
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self.toggle()
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(48, 28)
