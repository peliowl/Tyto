"""TButton atom component: a versatile button with multiple visual types.

Supports Primary, Default, Dashed, Text, Tertiary, Info, Success, Warning,
and Error types with size variants, loading, disabled, ghost, round, circle,
block, and icon placement options.  Mixes in HoverEffect, ClickRipple,
FocusGlow, and Disabled behaviors for rich interaction feedback.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QIcon, QMouseEvent, QPainter, QPainterPath
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QStyle, QStyleOption, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.click_ripple import ClickRippleMixin
from tyto_ui_lib.common.traits.disabled import DisabledMixin
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color

# Simple circular-arc SVG used as the loading spinner icon.
_SPINNER_SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
    '<circle cx="8" cy="8" r="6" fill="none" stroke="{color}"'
    ' stroke-width="2" stroke-dasharray="28 10" stroke-linecap="round"/>'
    "</svg>"
)


class _SpinnerWidget(QWidget):
    """Internal widget that renders a rotating SVG spinner."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = "#333639"
        self._renderer = QSvgRenderer(
            _SPINNER_SVG_TEMPLATE.format(color=self._color).encode(), self,
        )
        self._angle: float = 0.0
        self.setFixedSize(QSize(16, 16))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._anim = QPropertyAnimation(self, b"angle", self)
        self._anim.setDuration(1000)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(360.0)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)

    def set_color(self, color: str) -> None:
        """Update the spinner stroke color and reload the SVG.

        Args:
            color: CSS color string (e.g. '#ffffff', 'rgba(255,255,255,0.82)').
        """
        if color == self._color:
            return
        self._color = color
        self._renderer.load(_SPINNER_SVG_TEMPLATE.format(color=color).encode())
        self.update()

    def _get_angle(self) -> float:
        return self._angle

    def _set_angle(self, value: float) -> None:
        self._angle = value
        self.update()

    angle = Property(float, _get_angle, _set_angle)  # type: ignore[assignment]

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Render the SVG spinner rotated by the current angle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2.0, self.height() / 2.0)
        painter.rotate(self._angle)
        painter.translate(-self.width() / 2.0, -self.height() / 2.0)
        self._renderer.render(painter, self.rect().toRectF())
        painter.end()

    def start(self) -> None:
        """Start the rotation animation."""
        self._anim.start()

    def stop(self) -> None:
        """Stop the rotation animation."""
        self._anim.stop()



class TButton(
    HoverEffectMixin,
    ClickRippleMixin,
    FocusGlowMixin,
    DisabledMixin,
    BaseWidget,
):
    """Button component supporting multiple visual types and style variants.

    Emits ``clicked`` on mouse release when not loading or disabled.
    Provides a loading state with an animated SVG spinner that blocks
    all click events.

    Args:
        text: Button label text.
        button_type: Visual type variant.
        size: Size variant (tiny/small/medium/large).
        loading: Whether the button starts in loading state.
        disabled: Whether the button starts disabled.
        circle: Render as a circle button (equal width/height).
        round: Render with fully rounded (capsule) corners.
        ghost: Transparent background with colored border/text.
        secondary: Secondary level style variant.
        tertiary: Tertiary level style variant.
        quaternary: Quaternary level style variant.
        strong: Bold font weight.
        block: Expand width to fill parent container.
        color: Custom primary color override.
        text_color: Custom text color override.
        bordered: Whether to show border (default True).
        icon: Optional QIcon to display.
        icon_placement: Icon position relative to text (left/right).
        attr_type: Native button type attribute.
        focusable: Whether the button can receive focus.
        parent: Optional parent widget.

    Signals:
        clicked: Emitted when the button is clicked (not loading, not disabled).

    Example:
        >>> btn = TButton("Submit", button_type=TButton.ButtonType.PRIMARY)
        >>> btn.clicked.connect(lambda: print("clicked"))
    """

    class ButtonType(str, Enum):
        """Visual type variants for TButton."""

        PRIMARY = "primary"
        DEFAULT = "default"
        DASHED = "dashed"
        TEXT = "text"
        TERTIARY = "tertiary"
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    class ButtonSize(str, Enum):
        """Size variants for TButton."""

        TINY = "tiny"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class IconPlacement(str, Enum):
        """Icon position relative to button text."""

        LEFT = "left"
        RIGHT = "right"

    class AttrType(str, Enum):
        """Native HTML button type attribute."""

        BUTTON = "button"
        SUBMIT = "submit"
        RESET = "reset"

    clicked = Signal()

    def __init__(
        self,
        text: str = "",
        button_type: ButtonType = ButtonType.DEFAULT,
        size: ButtonSize = ButtonSize.MEDIUM,
        loading: bool = False,
        disabled: bool = False,
        circle: bool = False,
        round: bool = False,
        ghost: bool = False,
        secondary: bool = False,
        tertiary: bool = False,
        quaternary: bool = False,
        strong: bool = False,
        block: bool = False,
        color: str | None = None,
        text_color: str | None = None,
        bordered: bool = True,
        icon: QIcon | None = None,
        icon_placement: IconPlacement = IconPlacement.LEFT,
        attr_type: AttrType = AttrType.BUTTON,
        focusable: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        # Initialise mixin resources
        self._init_hover_effect()
        self._init_click_ripple()
        self._init_focus_glow()
        self._init_disabled()

        self._button_type = button_type
        self._size = size
        self._loading = False
        self._text = text
        self._circle = circle
        self._round = round
        self._ghost = ghost
        self._secondary = secondary
        self._tertiary = tertiary
        self._quaternary = quaternary
        self._strong = strong
        self._block = block
        self._color = color
        self._text_color = text_color
        self._bordered = bordered
        self._icon = icon
        self._icon_placement = icon_placement
        self._attr_type = attr_type

        # Layout: [icon_left] [spinner] [label] [icon_right]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon label (left placement)
        self._icon_label_left = QLabel(self)
        self._icon_label_left.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label_left.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._icon_label_left.setVisible(False)
        self._layout.addWidget(self._icon_label_left)

        self._spinner = _SpinnerWidget(self)
        self._spinner.setVisible(False)
        self._layout.addWidget(self._spinner)

        self._label = QLabel(text, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)

        # Icon label (right placement)
        self._icon_label_right = QLabel(self)
        self._icon_label_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label_right.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._icon_label_right.setVisible(False)
        self._layout.addWidget(self._icon_label_right)

        # Apply dynamic properties for QSS selectors
        self.setProperty("buttonType", button_type.value)
        self.setProperty("buttonSize", size.value)
        self.setProperty("ghost", str(ghost).lower())
        self.setProperty("round", str(round).lower())
        self.setProperty("circle", str(circle).lower())
        self.setProperty("block", str(block).lower())
        self.setProperty("bordered", str(bordered).lower())
        self.setProperty("strong", str(strong).lower())
        self.setProperty("secondary", str(secondary).lower())
        self.setProperty("tertiaryLevel", str(tertiary).lower())
        self.setProperty("quaternary", str(quaternary).lower())

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Focusable
        if focusable:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Block mode
        if block:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, self.sizePolicy().verticalPolicy())

        # Custom color overrides via dynamic properties
        if color is not None:
            self.setProperty("customColor", color)
        if text_color is not None:
            self.setProperty("customTextColor", text_color)

        # Icon setup
        self._update_icon_display()

        # Circle mode
        self._apply_circle_geometry()

        # Apply initial states
        if loading:
            self.set_loading(True)
        if disabled:
            self.set_disabled(True)

        self.apply_theme()

    # -- Public properties --

    @property
    def button_type(self) -> ButtonType:
        """Return the current button type."""
        return self._button_type

    @property
    def size(self) -> ButtonSize:
        """Return the current button size."""
        return self._size

    @property
    def loading(self) -> bool:
        """Return whether the button is in loading state."""
        return self._loading

    @property
    def text(self) -> str:
        """Return the button label text."""
        return self._text

    @property
    def circle(self) -> bool:
        """Return whether the button is in circle mode."""
        return self._circle

    @property
    def is_round(self) -> bool:
        """Return whether the button has fully rounded corners."""
        return self._round

    @property
    def ghost(self) -> bool:
        """Return whether the button is in ghost mode."""
        return self._ghost

    @property
    def is_secondary(self) -> bool:
        """Return whether the button uses secondary level style."""
        return self._secondary

    @property
    def is_tertiary(self) -> bool:
        """Return whether the button uses tertiary level style."""
        return self._tertiary

    @property
    def is_quaternary(self) -> bool:
        """Return whether the button uses quaternary level style."""
        return self._quaternary

    @property
    def strong(self) -> bool:
        """Return whether the button uses bold font."""
        return self._strong

    @property
    def block(self) -> bool:
        """Return whether the button fills parent width."""
        return self._block

    @property
    def bordered(self) -> bool:
        """Return whether the button shows a border."""
        return self._bordered

    @property
    def icon_placement(self) -> IconPlacement:
        """Return the icon placement (left or right)."""
        return self._icon_placement

    @property
    def attr_type(self) -> AttrType:
        """Return the native button type attribute."""
        return self._attr_type

    # -- Public setters --

    def set_text(self, text: str) -> None:
        """Update the button label text.

        Args:
            text: New label string.
        """
        self._text = text
        self._label.setText(text)

    def set_button_type(self, button_type: ButtonType) -> None:
        """Update the button type variant and refresh styles.

        Args:
            button_type: New button type variant.
        """
        self._button_type = button_type
        self.setProperty("buttonType", button_type.value)
        self._repolish()

    def set_size(self, size: ButtonSize) -> None:
        """Change the button size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("buttonSize", size.value)
        self._repolish()
        self._apply_circle_geometry()

    def set_loading(self, loading: bool) -> None:
        """Enter or exit loading state.

        In loading state the spinner is shown and all clicks are blocked.
        For circle buttons, the label is hidden so the spinner centers.

        Args:
            loading: True to enter loading state, False to exit.
        """
        self._loading = loading
        self._spinner.setVisible(loading)
        if loading:
            self._spinner.start()
            self.setCursor(Qt.CursorShape.WaitCursor)
            # Hide label and icons in circle mode so spinner centers
            if self._circle:
                self._label.setVisible(False)
                self._icon_label_left.setVisible(False)
                self._icon_label_right.setVisible(False)
        else:
            self._spinner.stop()
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            # Restore label visibility
            if self._circle:
                self._label.setVisible(True)
                self._update_icon_display()

    def set_disabled(self, disabled: bool) -> None:
        """Enter or exit disabled state via DisabledMixin.

        Args:
            disabled: True to disable, False to enable.
        """
        self.set_disabled_style(disabled)

    def set_circle(self, circle: bool) -> None:
        """Enable or disable circle mode.

        Args:
            circle: True for circle button, False for normal.
        """
        self._circle = circle
        self.setProperty("circle", str(circle).lower())
        self._repolish()
        self._apply_circle_geometry()
        if self._color or self._text_color:
            self._apply_custom_colors()
        # If loading is active, update label visibility for circle mode
        if self._loading:
            if circle:
                self._label.setVisible(False)
                self._icon_label_left.setVisible(False)
                self._icon_label_right.setVisible(False)
            else:
                self._label.setVisible(True)

    def set_round(self, round_: bool) -> None:
        """Enable or disable fully rounded (capsule) corners.

        Args:
            round_: True for capsule shape, False for normal radius.
        """
        self._round = round_
        self.setProperty("round", str(round_).lower())
        self._repolish()
        self._apply_circle_geometry()
        if self._color or self._text_color:
            self._apply_custom_colors()

    def set_ghost(self, ghost: bool) -> None:
        """Enable or disable ghost mode (transparent bg + colored border/text).

        Args:
            ghost: True for ghost style, False for normal.
        """
        self._ghost = ghost
        self.setProperty("ghost", str(ghost).lower())
        self._repolish()

    def set_strong(self, strong: bool) -> None:
        """Enable or disable bold font weight.

        Args:
            strong: True for bold, False for normal weight.
        """
        self._strong = strong
        self.setProperty("strong", str(strong).lower())
        self._repolish()

    def set_block(self, block: bool) -> None:
        """Enable or disable block mode (fill parent width).

        Args:
            block: True to expand width, False for normal sizing.
        """
        self._block = block
        self.setProperty("block", str(block).lower())
        if block:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, self.sizePolicy().verticalPolicy())
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, self.sizePolicy().verticalPolicy())
        self._repolish()

    def set_color(self, color: str | None) -> None:
        """Set a custom primary color override.

        Applies an inline stylesheet for the background and border color.

        Args:
            color: CSS color string, or None to clear.
        """
        self._color = color
        self._apply_custom_colors()

    def set_text_color(self, text_color: str | None) -> None:
        """Set a custom text color override.

        Applies an inline stylesheet for the text color on both the
        button and its inner QLabel.

        Args:
            text_color: CSS color string, or None to clear.
        """
        self._text_color = text_color
        self._apply_custom_colors()

    def _apply_custom_colors(self) -> None:
        """Build and apply an inline stylesheet from _color and _text_color.

        For round/circle buttons, background and border are handled by
        the custom paintEvent, so only text color is set via QSS.
        """
        is_rounded = hasattr(self, "_circle") and (self._circle or self._round)
        parts: list[str] = []
        label_parts: list[str] = []
        if self._color and not is_rounded:
            parts.append(f"background-color: {self._color};")
            parts.append(f"border-color: {self._color};")
        if self._text_color:
            parts.append(f"color: {self._text_color};")
            label_parts.append(f"color: {self._text_color};")

        if parts:
            qss = "TButton {" + " ".join(parts) + "}"
            if label_parts:
                qss += " TButton > QLabel {" + " ".join(label_parts) + "}"
            self.setStyleSheet(qss)
        else:
            self.setStyleSheet("")
        self._repolish()
        self.update()

    def set_bordered(self, bordered: bool) -> None:
        """Show or hide the button border.

        Args:
            bordered: True to show border, False to hide.
        """
        self._bordered = bordered
        self.setProperty("bordered", str(bordered).lower())
        self._repolish()

    def set_icon(self, icon: QIcon | None, placement: IconPlacement = IconPlacement.LEFT) -> None:
        """Set or clear the button icon.

        Args:
            icon: QIcon instance, or None to remove.
            placement: Position relative to text (left or right).
        """
        self._icon = icon
        self._icon_placement = placement
        self._update_icon_display()

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this button.

        The global stylesheet (set by ThemeEngine.switch_theme) already
        contains the TButton rules including property selectors like
        ``[buttonType="primary"]``.  Per-widget setStyleSheet would
        shadow those rules and break class-level property selectors,
        so we only force a re-polish here and re-apply size geometry.
        """
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        if hasattr(self, "_circle"):
            self._apply_circle_geometry()
        if hasattr(self, "_icon"):
            self._update_icon_display()
        # Update spinner color from theme tokens
        if hasattr(self, "_spinner"):
            self._update_spinner_color()
        self._repolish()

    # -- Event overrides --

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Render the button background and border.

        For circle/round modes, bypasses QSS border rendering and draws
        the background fill and border stroke manually using a rounded
        QPainterPath.  This ensures the border follows the same curve as
        the clip and hover/pressed border-color changes are visible at
        the corners.  For normal buttons, delegates to the standard
        QSS-based PE_Widget drawing.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        is_rounded = hasattr(self, "_circle") and (self._circle or self._round)

        if is_rounded:
            w, h = float(self.width()), float(self.height())
            if self._circle:
                radius = min(w, h) / 2.0
            else:
                radius = h / 2.0

            # Read colours from the QSS-resolved palette via QStyleOption
            opt = QStyleOption()
            opt.initFrom(self)

            # Resolve background and border from the style
            bg = opt.palette.window().color()
            border_color = opt.palette.mid().color()

            # Try to get actual QSS-resolved colors from the widget's style
            # by reading the rendered properties
            try:
                engine = ThemeEngine.instance()
                tokens = engine.current_tokens()
                if tokens:
                    from PySide6.QtGui import QColor

                    # Determine background and border based on button type and state
                    colors = tokens.colors
                    bt = self._button_type.value

                    # Background
                    if bt == "primary":
                        bg = parse_color(colors["primary"])
                    elif bt == "text":
                        bg = QColor(Qt.GlobalColor.transparent)
                    elif bt == "tertiary":
                        bg = parse_color(colors["bg_elevated"])
                    elif bt in ("info", "success", "warning", "error"):
                        bg = parse_color(colors[bt])
                    else:
                        bg = parse_color(colors["bg_default"])

                    # Border
                    if bt == "primary":
                        border_color = parse_color(colors["primary"])
                    elif bt == "text":
                        border_color = QColor(Qt.GlobalColor.transparent)
                    elif bt in ("info", "success", "warning", "error"):
                        border_color = parse_color(colors[bt])
                    else:
                        border_color = parse_color(colors["border"])

                    # Ghost override
                    if self._ghost:
                        bg = QColor(Qt.GlobalColor.transparent)

                    # Hover state override
                    if self.underMouse() and self.isEnabled():
                        if bt == "primary":
                            bg = parse_color(colors["primary_hover"])
                            border_color = parse_color(colors["primary_hover"])
                        elif bt == "dashed":
                            border_color = parse_color(colors["primary_hover"])
                        elif bt == "text":
                            bg = parse_color(colors["bg_elevated"])
                        elif bt == "info":
                            bg = parse_color(colors["info_hover"])
                            border_color = parse_color(colors["info_hover"])
                        else:
                            border_color = parse_color(colors["primary_hover"])

                        if self._ghost:
                            bg = QColor(Qt.GlobalColor.transparent)

                    # Custom color override
                    if self._color:
                        bg = parse_color(self._color)
                        border_color = parse_color(self._color)
                        if self._ghost:
                            bg = QColor(Qt.GlobalColor.transparent)
            except Exception:
                pass

            # Draw rounded background
            path = QPainterPath()
            inset = 0.5  # half border width
            path.addRoundedRect(inset, inset, w - 2 * inset, h - 2 * inset, radius, radius)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg)
            painter.drawPath(path)

            # Draw rounded border
            from PySide6.QtGui import QPen

            bt_val = self._button_type.value
            if bt_val == "dashed":
                pen = QPen(border_color, 1.0, Qt.PenStyle.DashLine)
            elif bt_val == "text" or not self._bordered:
                pen = QPen(Qt.PenStyle.NoPen)
            else:
                pen = QPen(border_color, 1.0)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        else:
            opt = QStyleOption()
            opt.initFrom(self)
            self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Block press events when loading; otherwise delegate to mixins."""
        if self._loading:
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit ``clicked`` on release when not loading/disabled."""
        if self._loading:
            event.accept()
            return
        super().mouseReleaseEvent(event)
        if self.isEnabled() and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size based on current size variant."""
        # Try to get height from tokens for accurate sizing
        try:
            engine = ThemeEngine.instance()
            tokens = engine.current_tokens()
            if tokens and tokens.component_sizes:
                size_data = tokens.component_sizes.get(self._size.value, {})
                h = size_data.get("height", 34)
                return QSize(80, h)
        except Exception:
            pass
        size_map = {
            self.ButtonSize.TINY: QSize(60, 22),
            self.ButtonSize.SMALL: QSize(70, 28),
            self.ButtonSize.MEDIUM: QSize(80, 34),
            self.ButtonSize.LARGE: QSize(90, 40),
        }
        return size_map.get(self._size, QSize(80, 34))

    # -- Private helpers --

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _update_spinner_color(self) -> None:
        """Set the spinner stroke color based on the current theme and button type.

        For button types with colored backgrounds (primary, info, success,
        warning, error), the spinner uses white. For other types, it uses
        the theme's primary color for better visibility.
        """
        try:
            engine = ThemeEngine.instance()
            tokens = engine.current_tokens()
            if not tokens:
                return
            bt = self._button_type.value
            colored_types = {"primary", "info", "success", "warning", "error"}
            if bt in colored_types and not self._ghost:
                color = "#ffffff"
            else:
                # Use primary color for the spinner — it's always a hex value
                # and provides good contrast in both light and dark modes
                color = str(tokens.colors.get("primary", "#18a058"))
            self._spinner.set_color(color)
        except Exception:
            pass

    def _update_icon_display(self) -> None:
        """Update icon label visibility and pixmap based on current icon/placement."""
        icon_size = 16  # Default icon size
        # Try to get icon size from tokens
        try:
            engine = ThemeEngine.instance()
            tokens = engine.current_tokens()
            if tokens and tokens.component_sizes:
                size_data = tokens.component_sizes.get(self._size.value, {})
                icon_size = size_data.get("icon_size", 16)
        except Exception:
            pass

        self._icon_label_left.setVisible(False)
        self._icon_label_right.setVisible(False)

        if self._icon is not None:
            pixmap = self._icon.pixmap(QSize(icon_size, icon_size))
            if self._icon_placement == self.IconPlacement.LEFT:
                self._icon_label_left.setPixmap(pixmap)
                self._icon_label_left.setFixedSize(QSize(icon_size, icon_size))
                self._icon_label_left.setVisible(True)
            else:
                self._icon_label_right.setPixmap(pixmap)
                self._icon_label_right.setFixedSize(QSize(icon_size, icon_size))
                self._icon_label_right.setVisible(True)

    def _apply_size_from_tokens(self) -> None:
        """Enforce button height and horizontal padding from design tokens."""
        if not hasattr(self, "_size"):
            return
        try:
            engine = ThemeEngine.instance()
            tokens = engine.current_tokens()
            if tokens and tokens.component_sizes:
                size_data = tokens.component_sizes.get(self._size.value, {})
                h = size_data.get("height", 0)
                if h > 0:
                    self.setFixedHeight(h)
                pad_h = size_data.get("padding_h", 0)
                if pad_h > 0:
                    self._layout.setContentsMargins(pad_h, 0, pad_h, 0)
        except Exception:
            pass

    def _apply_circle_geometry(self) -> None:
        """Apply fixed square geometry when circle mode is active."""
        if not hasattr(self, "_circle"):
            return
        if self._circle:
            hint = self.sizeHint()
            side = hint.height()
            self.setFixedSize(QSize(side, side))
            # Zero out layout margins so content centers in the square
            self._layout.setContentsMargins(0, 0, 0, 0)
            self._layout.setSpacing(0)
            # Scale spinner to match button size
            spinner_size = max(12, side // 3)
            self._spinner.setFixedSize(QSize(spinner_size, spinner_size))
        elif self._round:
            # Remove fixed size constraint but keep height from tokens
            self.setMinimumSize(QSize(0, 0))
            self.setMaximumSize(QSize(16777215, 16777215))
            self._layout.setSpacing(6)
            self._spinner.setFixedSize(QSize(16, 16))
            self._apply_size_from_tokens()
            self._apply_round_padding()
        else:
            # Remove fixed size constraint, apply token height + padding
            self.setMinimumSize(QSize(0, 0))
            self.setMaximumSize(QSize(16777215, 16777215))
            self._layout.setSpacing(6)
            self._spinner.setFixedSize(QSize(16, 16))
            self._apply_size_from_tokens()


    def _apply_round_padding(self) -> None:
        """Add extra horizontal padding for round buttons.

        The large border-radius on capsule buttons eats into the content
        area, so the internal layout needs extra left/right margins to
        keep text away from the curved edges.
        """
        try:
            engine = ThemeEngine.instance()
            tokens = engine.current_tokens()
            if tokens and tokens.component_sizes:
                size_data = tokens.component_sizes.get(self._size.value, {})
                h = size_data.get("height", 34)
                extra = h // 2
                self._layout.setContentsMargins(extra, 0, extra, 0)
                return
        except Exception:
            pass
        self._layout.setContentsMargins(17, 0, 17, 0)
