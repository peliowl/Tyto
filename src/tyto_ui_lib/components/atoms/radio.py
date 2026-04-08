"""TRadio, TRadioButton, and TRadioGroup atom components.

TRadio provides a single radio button with a smooth ring-scale animation,
size variants, and disabled state support.
TRadioButton provides a button-style radio for segmented button groups.
TRadioGroup manages mutual exclusion across TRadio or TRadioButton instances,
with support for button mode layout.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.disabled import DisabledMixin
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


# Indicator pixel sizes per RadioSize variant.
_INDICATOR_SIZES: dict[str, int] = {
    "small": 14,
    "medium": 16,
    "large": 20,
}

# Label font sizes per RadioSize variant.
_LABEL_FONT_SIZES: dict[str, int] = {
    "small": 12,
    "medium": 14,
    "large": 16,
}


class _RadioIndicator(QWidget):
    """Internal widget that paints the radio circle with a scale animation.

    Self-paints the border ring and inner dot using theme-driven colors,
    ensuring visibility in both light and dark modes.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("radio_indicator")
        self.setFixedSize(QSize(16, 16))
        self._progress: float = 0.0

        # Theme-driven colors (set by TRadio._update_indicator_colors)
        self._bg_color = QColor("#ffffff")
        self._border_color = QColor("#e0e0e6")
        self._checked_color = QColor("#18a058")

        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, value: float) -> None:
        self._progress = value
        self.update()

    progress = Property(float, _get_progress, _set_progress)  # type: ignore[assignment]

    def set_checked(self, checked: bool) -> None:
        """Update the visual state with a ring-scale animation.

        Args:
            checked: True to show the inner dot, False to hide it.
        """
        target = 1.0 if checked else 0.0
        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(target)
        self._anim.start()

    def set_indicator_size(self, px: int) -> None:
        """Resize the indicator square.

        Args:
            px: Side length in pixels.
        """
        self.setFixedSize(QSize(px, px))

    def set_colors(self, bg_color: str, border_color: str, checked_color: str) -> None:
        """Update the theme-driven colors used for painting.

        Args:
            bg_color: Background color for the indicator circle.
            border_color: Border color for unchecked state.
            checked_color: Border and inner dot color for checked state.
        """
        self._bg_color = QColor(bg_color)
        self._border_color = QColor(border_color)
        self._checked_color = QColor(checked_color)
        self.update()

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the border ring and inner filled circle scaled by current progress."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0

        # Interpolate border color: unchecked -> checked color
        p = self._progress
        if p > 0.01:
            border = QColor(
                int(self._border_color.red() + (self._checked_color.red() - self._border_color.red()) * p),
                int(self._border_color.green() + (self._checked_color.green() - self._border_color.green()) * p),
                int(self._border_color.blue() + (self._checked_color.blue() - self._border_color.blue()) * p),
                int(self._border_color.alpha() + (self._checked_color.alpha() - self._border_color.alpha()) * p),
            )
        else:
            border = self._border_color

        # Draw outer border ring
        pen_width = 2.0
        painter.setPen(QPen(border, pen_width))
        painter.setBrush(QBrush(self._bg_color))
        radius = (min(w, h) - pen_width) / 2.0
        painter.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))

        # Draw inner filled dot when checked (scaled by progress)
        if p > 0.01:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._checked_color)
            max_radius = min(w, h) / 4.5
            r = max_radius * p
            painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        painter.end()



class TRadio(
    HoverEffectMixin,
    FocusGlowMixin,
    DisabledMixin,
    BaseWidget,
):
    """Radio button component with ring-scale animation, size variants, and disabled state.

    Emits ``toggled`` when the checked state changes. Clicking an unchecked
    radio selects it. Use TRadioGroup for mutual exclusion across radios.

    Args:
        label: Text label displayed next to the radio indicator.
        value: Arbitrary value associated with this radio option.
        checked: Whether the radio starts in checked state.
        size: Size variant (small / medium / large).
        disabled: Whether the radio starts disabled.
        name: Native radio name attribute.
        parent: Optional parent widget.

    Signals:
        toggled: Emitted with the new boolean checked state.

    Example:
        >>> radio = TRadio("Option A", value="a", size=TRadio.RadioSize.SMALL)
        >>> radio.toggled.connect(lambda c: print(f"Checked: {c}"))
    """

    class RadioSize(str, Enum):
        """Size variants for TRadio."""

        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    toggled = Signal(bool)

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        checked: bool = False,
        size: RadioSize = RadioSize.MEDIUM,
        disabled: bool = False,
        name: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._init_hover_effect()
        self._init_focus_glow()
        self._init_disabled()

        self._checked = False
        self._value = value
        self._label_text = label
        self._size = size
        self._disabled = disabled
        self._name = name

        # Layout: [indicator] [label]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

        self._indicator = _RadioIndicator(self)
        self._layout.addWidget(self._indicator)

        self._label = QLabel(label, self)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)
        self._layout.addStretch()

        # Dynamic properties for QSS
        self.setProperty("checked", False)
        self.setProperty("radioSize", size.value)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply size variant
        self._apply_size()

        if checked:
            self.set_checked(True)

        # Apply disabled after everything is set up
        if disabled:
            self.set_disabled(True)

        self.apply_theme()

    # -- Public properties --

    @property
    def value(self) -> Any:
        """Return the value associated with this radio."""
        return self._value

    @property
    def size(self) -> RadioSize:
        """Return the current size variant."""
        return self._size

    @property
    def name(self) -> str:
        """Return the native radio name attribute."""
        return self._name

    # -- Public API --

    def is_checked(self) -> bool:
        """Return whether this radio is currently checked.

        Returns:
            True if checked, False otherwise.
        """
        return self._checked

    def set_checked(self, checked: bool) -> None:
        """Set the checked state programmatically.

        Args:
            checked: True to check, False to uncheck.
        """
        if checked == self._checked:
            return
        self._checked = checked
        self._indicator.set_checked(checked)
        self.setProperty("checked", checked)
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled.emit(checked)

    def set_size(self, size: RadioSize) -> None:
        """Change the radio size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("radioSize", size.value)
        self._apply_size()
        self._repolish()

    def set_disabled(self, disabled: bool) -> None:
        """Enter or exit disabled state.

        Args:
            disabled: True to disable, False to enable.
        """
        self._disabled = disabled
        self.set_disabled_style(disabled)

    def is_disabled(self) -> bool:
        """Return whether the radio is currently disabled."""
        return self._disabled

    def set_name(self, name: str) -> None:
        """Set the native radio name attribute.

        Args:
            name: The name string.
        """
        self._name = name

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this radio and update indicator colors."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("radio.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)

            # Push current theme colors into the indicator for self-painting
            self._update_indicator_colors()
            # Update label color from theme
            self._apply_size()
        except Exception:
            pass

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle click to select this radio. Blocked when disabled."""
        if self._disabled:
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and not self._checked:
            self.set_checked(True)
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size."""
        return QSize(120, 24)

    # -- Private --

    def _apply_size(self) -> None:
        """Apply indicator and label sizing for the current size variant."""
        indicator_px = _INDICATOR_SIZES.get(self._size.value, 16)
        font_px = _LABEL_FONT_SIZES.get(self._size.value, 14)
        self._indicator.set_indicator_size(indicator_px)

        # Include text color from theme so the inline stylesheet does not
        # override the inherited color (fixes dark-mode invisible text).
        engine = ThemeEngine.instance()
        text_color = ""
        if engine.current_theme():
            try:
                text_color = str(engine.get_token("colors", "text_primary"))
            except (RuntimeError, KeyError):
                pass
        if text_color:
            self._label.setStyleSheet(f"font-size: {font_px}px; color: {text_color};")
        else:
            self._label.setStyleSheet(f"font-size: {font_px}px;")

    def _update_indicator_colors(self) -> None:
        """Push current theme colors into the indicator for self-painting."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            bg = str(engine.get_token("colors", "bg_default"))
            border = str(engine.get_token("colors", "border"))
            primary = str(engine.get_token("colors", "primary"))
        except (RuntimeError, KeyError):
            return
        self._indicator.set_colors(bg, border, primary)

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class TRadioButton(
    HoverEffectMixin,
    FocusGlowMixin,
    DisabledMixin,
    BaseWidget,
):
    """Button-style radio component for use in RadioGroup button mode.

    Renders as a segmented button rather than a traditional radio circle.
    Use within a TRadioGroup for mutual exclusion.

    Args:
        label: Text label displayed on the button.
        value: Arbitrary value associated with this radio option.
        checked: Whether the button starts in checked state.
        size: Size variant (small / medium / large).
        disabled: Whether the button starts disabled.
        parent: Optional parent widget.

    Signals:
        toggled: Emitted with the new boolean checked state.

    Example:
        >>> rb = TRadioButton("Beijing", value="bj")
        >>> rb.toggled.connect(lambda c: print(f"Checked: {c}"))
    """

    toggled = Signal(bool)

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        checked: bool = False,
        size: TRadio.RadioSize = TRadio.RadioSize.MEDIUM,
        disabled: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._init_hover_effect()
        self._init_focus_glow()
        self._init_disabled()

        self._checked = False
        self._value = value
        self._label_text = label
        self._size = size
        self._disabled = disabled

        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(label, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)

        # Dynamic properties for QSS
        self.setProperty("checked", False)
        self.setProperty("radioButtonSize", size.value)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if checked:
            self.set_checked(True)

        if disabled:
            self.set_disabled(True)

        self.apply_theme()

    # -- Public properties --

    @property
    def value(self) -> Any:
        """Return the value associated with this radio button."""
        return self._value

    @property
    def size(self) -> TRadio.RadioSize:
        """Return the current size variant."""
        return self._size

    # -- Public API --

    def is_checked(self) -> bool:
        """Return whether this radio button is currently checked.

        Returns:
            True if checked, False otherwise.
        """
        return self._checked

    def set_checked(self, checked: bool) -> None:
        """Set the checked state programmatically.

        Args:
            checked: True to check, False to uncheck.
        """
        if checked == self._checked:
            return
        self._checked = checked
        self.setProperty("checked", checked)
        self._repolish()
        self.toggled.emit(checked)

    def set_size(self, size: TRadio.RadioSize) -> None:
        """Change the radio button size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("radioButtonSize", size.value)
        self._repolish()

    def set_disabled(self, disabled: bool) -> None:
        """Enter or exit disabled state.

        Args:
            disabled: True to disable, False to enable.
        """
        self._disabled = disabled
        self.set_disabled_style(disabled)

    def is_disabled(self) -> bool:
        """Return whether the radio button is currently disabled."""
        return self._disabled

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this radio button."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("radiobutton.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle click to select this radio button. Blocked when disabled."""
        if self._disabled:
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and not self._checked:
            self.set_checked(True)
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size."""
        size_map = {
            TRadio.RadioSize.SMALL: QSize(70, 28),
            TRadio.RadioSize.MEDIUM: QSize(80, 34),
            TRadio.RadioSize.LARGE: QSize(90, 40),
        }
        return size_map.get(self._size, QSize(80, 34))

    # -- Private --

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class TRadioGroup(BaseWidget):
    """Radio group manager that enforces mutual exclusion.

    Manages a collection of TRadio or TRadioButton instances so that at most
    one is checked at any time. Supports button mode layout when containing
    TRadioButton items.

    Args:
        name: Unified name for all radios in the group.
        size: Unified size for all child radios (None = use each radio's own size).
        disabled: Whether all child radios start disabled.
        default_value: Value of the radio to pre-select.
        parent: Optional parent widget.

    Signals:
        selection_changed: Emitted with the value of the newly selected radio.

    Example:
        >>> group = TRadioGroup(size=TRadio.RadioSize.SMALL)
        >>> group.add_radio(TRadio("A", value="a"))
        >>> group.add_radio(TRadio("B", value="b"))
        >>> group.selection_changed.connect(lambda v: print(f"Selected: {v}"))
    """

    selection_changed = Signal(object)

    def __init__(
        self,
        name: str = "",
        size: TRadio.RadioSize | None = None,
        disabled: bool = False,
        default_value: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._radios: list[TRadio | TRadioButton] = []
        self._name = name
        self._group_size = size
        self._group_disabled = disabled
        self._default_value = default_value
        self._button_mode = False

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # Button mode uses horizontal layout; will switch on first TRadioButton
        self._h_layout = QHBoxLayout()
        self._h_layout.setContentsMargins(0, 0, 0, 0)
        self._h_layout.setSpacing(0)

    def add_radio(self, radio: TRadio | TRadioButton) -> None:
        """Add a radio or radio button to this group.

        Connects the radio's toggled signal to the mutual exclusion logic.
        Applies group-level name, size, and disabled settings.

        Args:
            radio: The TRadio or TRadioButton instance to add.
        """
        self._radios.append(radio)

        # Detect button mode
        if isinstance(radio, TRadioButton):
            if not self._button_mode:
                self._switch_to_button_mode()
            self._h_layout.addWidget(radio)
        else:
            if self._button_mode:
                # Mixed mode: add to horizontal layout anyway
                self._h_layout.addWidget(radio)
            else:
                self._layout.addWidget(radio)

        # Apply group-level overrides
        if self._group_size is not None:
            radio.set_size(self._group_size)
        if self._group_disabled:
            radio.set_disabled(True)
        if self._name and isinstance(radio, TRadio):
            radio.set_name(self._name)

        # Pre-select if matches default_value
        if self._default_value is not None and radio.value == self._default_value and not radio.is_checked():
            radio.set_checked(True)

        radio.toggled.connect(lambda checked, r=radio: self._on_radio_toggled(r, checked))

    def get_selected_value(self) -> Any:
        """Return the value of the currently selected radio.

        Returns:
            The value of the checked radio, or None if none is selected.
        """
        for radio in self._radios:
            if radio.is_checked():
                return radio.value
        return None

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable all radios in the group.

        Args:
            disabled: True to disable all, False to enable all.
        """
        self._group_disabled = disabled
        for radio in self._radios:
            radio.set_disabled(disabled)

    def set_size(self, size: TRadio.RadioSize) -> None:
        """Set a unified size for all radios in the group.

        Args:
            size: The size variant to apply.
        """
        self._group_size = size
        for radio in self._radios:
            radio.set_size(size)

    def is_button_mode(self) -> bool:
        """Return True if group contains TRadioButton items.

        Returns:
            True if in button mode, False otherwise.
        """
        return self._button_mode

    # -- Private --

    def _switch_to_button_mode(self) -> None:
        """Switch layout from vertical to horizontal compact for button mode."""
        self._button_mode = True
        # Move any existing radios from vertical to horizontal layout
        for radio in self._radios:
            self._layout.removeWidget(radio)
            self._h_layout.addWidget(radio)
        self._layout.addLayout(self._h_layout)

    def _on_radio_toggled(self, source: TRadio | TRadioButton, checked: bool) -> None:
        """Handle a radio being toggled; enforce mutual exclusion.

        Args:
            source: The radio that was toggled.
            checked: The new checked state.
        """
        if not checked:
            return

        for radio in self._radios:
            if radio is not source and radio.is_checked():
                radio.set_checked(False)

        self.selection_changed.emit(source.value)
