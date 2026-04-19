"""TTag atom component: a label tag with size, color type, and closable support.

Supports Tiny/Small/Medium/Large sizes and Default/Primary/Success/Info/Warning/Error
color types. Optionally displays a close button that emits ``closed``.
Supports checkable mode, disabled state, custom colors, round/bordered/strong variants.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


class TTag(BaseWidget):
    """Tag component for displaying categorised labels or status markers.

    Args:
        text: Tag label text.
        tag_type: Color type variant.
        size: Size variant.
        closable: Whether to show a close button.
        round: Whether to render with fully rounded corners.
        disabled: Whether the tag is disabled.
        bordered: Whether to show a border.
        color: Custom color dict with keys 'color', 'border_color', 'text_color'.
        checkable: Whether the tag supports click-to-toggle checked state.
        checked: Initial checked state (only used when checkable=True).
        strong: Whether to render text in bold.
        parent: Optional parent widget.

    Signals:
        closed: Emitted when the close button is clicked.
        checked_changed: Emitted with the new boolean checked state when toggled.

    Example:
        >>> tag = TTag("New", tag_type=TTag.TagType.PRIMARY, closable=True)
        >>> tag.closed.connect(lambda: print("tag closed"))
        >>> checkable_tag = TTag("Filter", checkable=True)
        >>> checkable_tag.checked_changed.connect(lambda v: print(f"checked: {v}"))
    """

    class TagSize(str, Enum):
        """Size variants for TTag."""

        TINY = "tiny"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    class TagType(str, Enum):
        """Color type variants for TTag."""

        DEFAULT = "default"
        PRIMARY = "primary"
        SUCCESS = "success"
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"

    closed = Signal(object)
    checked_changed = Signal(bool)
    mouse_enter = Signal(object)
    mouse_leave = Signal(object)

    def __init__(
        self,
        text: str = "",
        tag_type: TagType = TagType.DEFAULT,
        size: TagSize = TagSize.MEDIUM,
        closable: bool = False,
        round: bool = False,
        disabled: bool = False,
        bordered: bool = True,
        color: dict[str, str] | None = None,
        checkable: bool = False,
        checked: bool = False,
        strong: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        # Initialize instance attributes BEFORE super().__init__() because
        # BaseWidget.__init__ calls apply_theme() which references them.
        self._tag_type = tag_type
        self._size = size
        self._closable = closable
        self._text = text
        self._round = round
        self._disabled = disabled
        self._bordered = bordered
        self._color = color
        self._checkable = checkable
        self._checked = checked
        self._strong = strong

        super().__init__(parent)

        # Layout: [label] [close_btn?]
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(0)
        # Content margins are set in _update_layout_margins() via apply_theme()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(text, self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)

        self._close_btn: QPushButton | None = None
        if closable:
            self._close_btn = QPushButton("\u2715", self)  # Unicode multiplication sign as close icon
            self._close_btn.setObjectName("tag_close_btn")
            self._close_btn.setFixedSize(QSize(16, 16))
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self._on_close_clicked)
            self._layout.addWidget(self._close_btn)

        # Dynamic properties for QSS selectors
        self.setProperty("tagType", tag_type.value)
        self.setProperty("tagSize", size.value)
        self.setProperty("round", str(round).lower())
        self.setProperty("bordered", str(bordered).lower())
        self.setProperty("strong", str(strong).lower())
        self.setProperty("checkable", str(checkable).lower())
        self.setProperty("checked", str(checked).lower())
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Checkable cursor
        if checkable and not disabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Disabled state
        if disabled:
            self._apply_disabled_visual()

        # Custom color override
        if color:
            self._apply_custom_color(color)

        self.apply_theme()

    # -- Public properties --

    @property
    def tag_type(self) -> TagType:
        """Return the current color type."""
        return self._tag_type

    @property
    def size(self) -> TagSize:
        """Return the current size variant."""
        return self._size

    @property
    def text(self) -> str:
        """Return the tag label text."""
        return self._text

    @property
    def closable(self) -> bool:
        """Return whether the tag has a close button."""
        return self._closable

    @property
    def is_round(self) -> bool:
        """Return whether the tag has fully rounded corners."""
        return self._round

    @property
    def disabled(self) -> bool:
        """Return whether the tag is disabled."""
        return self._disabled

    @property
    def bordered(self) -> bool:
        """Return whether the tag shows a border."""
        return self._bordered

    @property
    def strong(self) -> bool:
        """Return whether the tag text is bold."""
        return self._strong

    @property
    def checkable(self) -> bool:
        """Return whether the tag supports checkable mode."""
        return self._checkable

    # -- Public setters --

    def set_tag_type(self, tag_type: TagType) -> None:
        """Update the tag color type and refresh styles.

        Args:
            tag_type: New color type variant.
        """
        self._tag_type = tag_type
        self.setProperty("tagType", tag_type.value)
        self._repolish()

    def set_size(self, size: TagSize) -> None:
        """Update the tag size variant and refresh styles.

        Args:
            size: New size variant.
        """
        self._size = size
        self.setProperty("tagSize", size.value)
        self._update_layout_margins()
        self._repolish()
        self.updateGeometry()

    def set_text(self, text: str) -> None:
        """Update the tag label text.

        Args:
            text: New label string.
        """
        self._text = text
        self._label.setText(text)
    def set_tag_type(self, tag_type: TagType) -> None:
        """Update the tag color type and refresh styles.

        Args:
            tag_type: New color type variant.
        """
        self._tag_type = tag_type
        self.setProperty("tagType", tag_type.value)
        self._repolish()



    def set_round(self, round_: bool) -> None:
        """Enable or disable fully rounded corners.

        Args:
            round_: True for capsule shape.
        """
        self._round = round_
        self.setProperty("round", str(round_).lower())
        self.apply_theme()

    def set_disabled(self, disabled: bool) -> None:
        """Enable or disable the tag.

        Args:
            disabled: True to disable interactions.
        """
        self._disabled = disabled
        self.setProperty("disabled", str(disabled).lower())
        if disabled:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            if self._checkable:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.unsetCursor()
        self._repolish()

    def set_bordered(self, bordered: bool) -> None:
        """Enable or disable the border.

        Args:
            bordered: True to show border.
        """
        self._bordered = bordered
        self.setProperty("bordered", str(bordered).lower())
        self._repolish()

    def set_color(self, color: dict[str, str] | None) -> None:
        """Set custom color overrides.

        Args:
            color: Dict with optional keys 'color', 'border_color', 'text_color',
                   or None to clear custom colors.
        """
        self._color = color
        if color:
            self._apply_custom_color(color)
        else:
            self.setStyleSheet("")
        self._repolish()

    def set_checked(self, checked: bool) -> None:
        """Set the checked state (only effective when checkable=True).

        Args:
            checked: New checked state.
        """
        if not self._checkable:
            return
        old = self._checked
        self._checked = checked
        self.setProperty("checked", str(checked).lower())
        self._repolish()
        if old != checked:
            self.checked_changed.emit(checked)
            self._emit_bus_event("checked_changed", checked)

    def is_checked(self) -> bool:
        """Return the current checked state.

        Returns:
            True if checked, False otherwise.
        """
        return self._checked

    def set_strong(self, strong: bool) -> None:
        """Enable or disable bold text.

        Args:
            strong: True for bold font weight.
        """
        self._strong = strong
        self.setProperty("strong", str(strong).lower())
        self._repolish()

    def set_checkable(self, checkable: bool) -> None:
        """Enable or disable checkable toggle mode.

        Args:
            checkable: True to allow click-to-toggle checked state.
        """
        self._checkable = checkable
        if not checkable:
            self._checked = False
        self.setProperty("checkable", str(checkable).lower())
        self.setProperty("checked", str(self._checked).lower())
        if checkable and not self._disabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        elif not self._disabled:
            self.unsetCursor()
        self._repolish()

    # -- Event handling --

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        """Handle mouse press for checkable toggle."""
        if self._checkable and not self._disabled:
            self.set_checked(not self._checked)
        super().mousePressEvent(event)

    def enterEvent(self, event: Any) -> None:  # noqa: N802
        """Emit mouse_enter when the mouse enters the tag area."""
        self.mouse_enter.emit(event)
        self._emit_bus_event("mouse_enter", event)
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:  # noqa: N802
        """Emit mouse_leave when the mouse leaves the tag area."""
        self.mouse_leave.emit(event)
        self._emit_bus_event("mouse_leave", event)
        super().leaveEvent(event)

    # -- Private helpers --

    def _on_close_clicked(self) -> None:
        """Handle close button click: emit closed signal then hide the tag."""
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QMouseEvent

        synthetic = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(0, 0),
            QPointF(0, 0),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        self.closed.emit(synthetic)
        self._emit_bus_event("closed", synthetic)
        self.setVisible(False)


    def _apply_custom_color(self, color: dict[str, str]) -> None:
        """Apply custom color dict as inline stylesheet override.

        Args:
            color: Dict with optional keys 'color' (background), 'border_color', 'text_color'.
        """
        parts: list[str] = []
        if "color" in color:
            parts.append(f"background-color: {color['color']};")
        if "border_color" in color:
            parts.append(f"border-color: {color['border_color']};")
        if "text_color" in color:
            parts.append(f"color: {color['text_color']};")
        if parts:
            self.setStyleSheet("TTag { " + " ".join(parts) + " }")

    def _update_layout_margins(self) -> None:
        """Set layout content margins from Design Tokens based on current size.

        QSS ``padding`` on a widget with a child QHBoxLayout does not push
        the layout children inward.  We therefore mirror the intended
        horizontal padding via layout content margins so that the label
        (and close button) never touch the tag edges.
        """
        if not hasattr(self, "_layout"):
            return

        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens is None:
            return

        spacing = tokens.spacing

        # Determine vertical / horizontal padding that matches the QSS template
        if self._size == self.TagSize.TINY:
            pad_v = 0
            pad_h = spacing.get("small", 4)
        elif self._size == self.TagSize.SMALL:
            pad_v = 0
            pad_h = spacing.get("small", 4)
        elif self._size == self.TagSize.LARGE:
            pad_v = spacing.get("small", 4)
            pad_h = spacing.get("large", 16)
        else:  # MEDIUM (default)
            pad_v = spacing.get("small", 4)
            pad_h = spacing.get("medium", 8)

        self._layout.setContentsMargins(pad_h, pad_v, pad_h, pad_v)

        # Add a small gap between label and close button
        if self._close_btn is not None:
            self._layout.setSpacing(spacing.get("small", 4))

    def _repolish(self) -> None:
        """Force Qt to re-evaluate QSS property selectors."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this tag.

        The global stylesheet already contains TTag rules with property
        selectors.  We only re-polish to pick up changes and update
        layout margins to match the intended padding.
        """
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        # Re-apply custom color if set (it uses inline stylesheet)
        if self._color:
            self._apply_custom_color(self._color)
        self._update_layout_margins()
        self._repolish()
        self.updateGeometry()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size based on the current size variant."""
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens is not None and hasattr(tokens, "component_sizes"):
            sizes = tokens.component_sizes
            size_key = self._size.value
            if isinstance(sizes, dict) and size_key in sizes:
                entry = sizes[size_key]
                h = entry.get("height", 24) if isinstance(entry, dict) else 24
                return QSize(60, h)
        return QSize(60, 24)
