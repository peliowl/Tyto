"""TPopconfirm molecule component: lightweight popover confirmation dialog.

Appears near a trigger element, providing confirm/cancel actions as a
lighter alternative to modal dialogs.  Supports placement control,
fade-in/fade-out animation, outside-click dismissal, multiple trigger
modes (click/hover/focus/manual), icon control, and button customisation.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any

from PySide6.QtCore import (
    QEvent,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QCursor, QIcon, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.components.atoms.button import TButton
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color


class _PopconfirmContainer(QWidget):
    """Inner container that paints its own background and rounded border.

    Required because the parent popup uses WA_TranslucentBackground,
    which prevents QSS background-color from rendering on child widgets.
    """

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint rounded-rect background and border using theme tokens."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            engine = ThemeEngine.instance()
            bg = parse_color(str(engine.get_token("colors", "popover_color")))
            border_c = parse_color(str(engine.get_token("colors", "border")))
            radius = int(engine.get_token("radius", "medium"))
        except Exception:
            bg = QColor("#ffffff")
            border_c = QColor("#e0e0e6")
            radius = 4

        from PySide6.QtCore import QRectF

        pen = QPen(border_c)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(bg)
        rect = QRectF(0.5, 0.5, self.width() - 1.0, self.height() - 1.0)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()


class TPopconfirm(BaseWidget):
    """Lightweight popover confirmation dialog.

    Appears near the trigger element, providing confirm/cancel actions
    as a lighter alternative to modal dialogs.  Supports multiple trigger
    modes (click / hover / focus / manual), icon visibility control,
    custom button props, and per-action callbacks.

    Args:
        trigger: Widget that triggers the popconfirm.
        title: Confirmation prompt text.
        confirm_text: Text for the confirm button.
        cancel_text: Text for the cancel button.
        icon: Custom icon; defaults to a warning icon.
        placement: Popup position relative to the trigger.
        show_icon: Whether to display the prompt icon.
        positive_button_props: Extra TButton kwargs for the confirm button.
        negative_button_props: Extra TButton kwargs for the cancel button.
        trigger_mode: How the popup is triggered ("click"/"hover"/"focus"/"manual").
        on_positive_click: Callback invoked when confirm is clicked.
        on_negative_click: Callback invoked when cancel is clicked.
        parent: Optional parent widget.

    Signals:
        confirmed: Emitted when user clicks confirm button.
        cancelled: Emitted when user clicks cancel button.

    Example:
        >>> btn = TButton(text="Delete")
        >>> pop = TPopconfirm(trigger=btn, title="Are you sure?")
        >>> pop.confirmed.connect(lambda: print("Confirmed"))
    """

    class Placement(str, Enum):
        """Popup placement relative to the trigger element."""

        TOP = "top"
        BOTTOM = "bottom"
        LEFT = "left"
        RIGHT = "right"

    class TriggerMode(str, Enum):
        """How the popup is triggered."""

        CLICK = "click"
        HOVER = "hover"
        FOCUS = "focus"
        MANUAL = "manual"

    confirmed = Signal()
    cancelled = Signal()

    _POPUP_MARGIN = 8  # px gap between trigger and popup

    def __init__(
        self,
        trigger: QWidget | None = None,
        title: str = "确认操作？",
        confirm_text: str = "确认",
        cancel_text: str = "取消",
        icon: QIcon | None = None,
        placement: Placement = Placement.TOP,
        show_icon: bool = True,
        positive_button_props: dict[str, Any] | None = None,
        negative_button_props: dict[str, Any] | None = None,
        trigger_mode: str = "click",
        on_positive_click: Callable[[], None] | None = None,
        on_negative_click: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        self._trigger: QWidget | None = None
        self._title_text = title
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._icon = icon
        self._placement = placement
        self._popup: QWidget | None = None
        self._fade_anim: QPropertyAnimation | None = None
        self._fade_anim_connected = False  # Track whether finished signal is connected
        self._opacity_effect: QGraphicsOpacityEffect | None = None

        # V1.1.0 enhancement attributes
        self._show_icon = show_icon
        self._positive_button_props: dict[str, Any] = positive_button_props or {}
        self._negative_button_props: dict[str, Any] = negative_button_props or {}
        self._on_positive_click = on_positive_click
        self._on_negative_click = on_negative_click
        self._custom_icon_widget: QWidget | None = None

        # Cached popup internal widget references for reuse
        self._cached_title_label: QLabel | None = None
        self._cached_confirm_btn: TButton | None = None
        self._cached_cancel_btn: TButton | None = None
        self._popup_dirty = True  # Flag: rebuild popup content on next show

        # Validate trigger mode, fallback to CLICK
        try:
            self._trigger_mode = self.TriggerMode(trigger_mode)
        except ValueError:
            self._trigger_mode = self.TriggerMode.CLICK

        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if trigger is not None:
            self.set_trigger_widget(trigger)

        # Install global event filter for outside-click detection
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    # -- Public properties --

    @property
    def placement(self) -> Placement:
        """Return the current popup placement."""
        return self._placement

    @placement.setter
    def placement(self, value: Placement) -> None:
        """Set the popup placement."""
        self._placement = value

    @property
    def title(self) -> str:
        """Return the confirmation title text."""
        return self._title_text

    @title.setter
    def title(self, value: str) -> None:
        """Set the confirmation title text."""
        if self._title_text != value:
            self._title_text = value
            # Update cached label directly if popup exists, avoid full rebuild
            if self._cached_title_label is not None:
                self._cached_title_label.setText(value)

    @property
    def confirm_text(self) -> str:
        """Return the confirm button text."""
        return self._confirm_text

    @confirm_text.setter
    def confirm_text(self, value: str) -> None:
        """Set the confirm button text."""
        if self._confirm_text != value:
            self._confirm_text = value
            if self._cached_confirm_btn is not None:
                self._cached_confirm_btn.set_text(value)

    @property
    def cancel_text(self) -> str:
        """Return the cancel button text."""
        return self._cancel_text

    @cancel_text.setter
    def cancel_text(self, value: str) -> None:
        """Set the cancel button text."""
        if self._cancel_text != value:
            self._cancel_text = value
            if self._cached_cancel_btn is not None:
                self._cached_cancel_btn.set_text(value)

    @property
    def show_icon(self) -> bool:
        """Return whether the prompt icon is visible."""
        return self._show_icon

    @show_icon.setter
    def show_icon(self, value: bool) -> None:
        """Set whether the prompt icon is visible."""
        self._show_icon = value

    @property
    def trigger_mode(self) -> TriggerMode:
        """Return the current trigger mode."""
        return self._trigger_mode

    @trigger_mode.setter
    def trigger_mode(self, value: str | TriggerMode) -> None:
        """Set the trigger mode."""
        try:
            self._trigger_mode = self.TriggerMode(value) if isinstance(value, str) else value
        except ValueError:
            self._trigger_mode = self.TriggerMode.CLICK

    @property
    def positive_button_props(self) -> dict[str, Any]:
        """Return the confirm button custom props."""
        return self._positive_button_props

    @positive_button_props.setter
    def positive_button_props(self, value: dict[str, Any]) -> None:
        """Set the confirm button custom props."""
        self._positive_button_props = value
        self._popup_dirty = True

    @property
    def negative_button_props(self) -> dict[str, Any]:
        """Return the cancel button custom props."""
        return self._negative_button_props

    @negative_button_props.setter
    def negative_button_props(self, value: dict[str, Any]) -> None:
        """Set the cancel button custom props."""
        self._negative_button_props = value
        self._popup_dirty = True

    @property
    def on_positive_click(self) -> Callable[[], None] | None:
        """Return the confirm button callback."""
        return self._on_positive_click

    @on_positive_click.setter
    def on_positive_click(self, value: Callable[[], None] | None) -> None:
        """Set the confirm button callback."""
        self._on_positive_click = value

    @property
    def on_negative_click(self) -> Callable[[], None] | None:
        """Return the cancel button callback."""
        return self._on_negative_click

    @on_negative_click.setter
    def on_negative_click(self, value: Callable[[], None] | None) -> None:
        """Set the cancel button callback."""
        self._on_negative_click = value

    # -- Public methods --

    def set_trigger(self, trigger: QWidget) -> None:
        """Set or replace the trigger widget (backward-compat alias).

        Args:
            trigger: Widget that opens the popup.
        """
        self.set_trigger_widget(trigger)

    def set_trigger_widget(self, trigger: QWidget) -> None:
        """Set or replace the trigger widget.

        The trigger widget is re-parented into this component's layout.

        Args:
            trigger: Widget that opens the popup.
        """
        if self._trigger is not None:
            self.layout().removeWidget(self._trigger)

        self._trigger = trigger
        trigger.setParent(self)
        self.layout().addWidget(trigger)

    def set_icon(self, widget: QWidget | None) -> None:
        """Set a custom icon widget for the prompt.

        Args:
            widget: Custom icon widget, or None to revert to default.
        """
        self._custom_icon_widget = widget

    def set_positive_button_props(self, props: dict[str, Any]) -> None:
        """Set custom props for the confirm button.

        Args:
            props: Dict of TButton kwargs.
        """
        self._positive_button_props = props

    def set_negative_button_props(self, props: dict[str, Any]) -> None:
        """Set custom props for the cancel button.

        Args:
            props: Dict of TButton kwargs.
        """
        self._negative_button_props = props

    def show_popup(self) -> None:
        """Show the confirmation popup near the trigger element.

        Reuses a cached popup widget when possible to avoid the overhead
        of rebuilding the entire widget tree on every click.  The popup
        is only rebuilt when properties that affect the button layout
        (positive/negative_button_props) have changed.
        """
        if self._trigger is None:
            return

        # If popup is already visible, toggle it off
        if self._popup is not None and self._popup.isVisible():
            self.hide_popup()
            return

        # Build or reuse the cached popup
        if self._popup is None or self._popup_dirty:
            self._destroy_popup()
            self._popup = self._build_popup()
            self._popup_dirty = False
        else:
            # Reuse cached popup — just sync text properties
            if self._cached_title_label is not None:
                self._cached_title_label.setText(self._title_text)
            if self._cached_confirm_btn is not None:
                self._cached_confirm_btn.set_text(self._confirm_text)
            if self._cached_cancel_btn is not None:
                self._cached_cancel_btn.set_text(self._cancel_text)

        self._popup.show()
        self._popup.raise_()
        self._position_popup()
        self._fade_in()

        if not hasattr(self, "_reposition_timer"):
            from PySide6.QtCore import QTimer

            self._reposition_timer = QTimer(self)
            self._reposition_timer.setInterval(16)
            self._reposition_timer.timeout.connect(self._reposition_popup_tick)
        self._reposition_timer.start()

    def hide_popup(self) -> None:
        """Hide the confirmation popup (keeps it cached for reuse)."""
        if hasattr(self, "_reposition_timer"):
            self._reposition_timer.stop()
        if self._popup is not None:
            self._popup.hide()

    def _destroy_popup(self) -> None:
        """Destroy the cached popup and release all references."""
        if hasattr(self, "_reposition_timer"):
            self._reposition_timer.stop()
        if self._popup is not None:
            self._popup.hide()
            self._popup.deleteLater()
            self._popup = None
        self._cached_title_label = None
        self._cached_confirm_btn = None
        self._cached_cancel_btn = None
        self._opacity_effect = None
        self._fade_anim = None
        self._fade_anim_connected = False

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this popconfirm and cached popup."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("popconfirm.qss.j2")
            self.setStyleSheet(qss)
            if self._popup is not None:
                self._popup.setStyleSheet(qss)
                # Force container repaint for theme-aware background
                self._popup.update()
        except Exception:
            pass

    def sizeHint(self) -> QSize:  # noqa: N802
        """Provide a reasonable default size based on trigger."""
        if self._trigger is not None:
            return self._trigger.sizeHint()
        return QSize(100, 34)

    # -- Event filter --

    def eventFilter(self, obj: Any, event: QEvent) -> bool:  # noqa: N802
        """Handle trigger interactions and outside-click dismissal.

        Supports click, hover, focus, and manual trigger modes.
        Uses global cursor position against the popup geometry to
        reliably detect inside-popup clicks (bug fix for 66.12).

        Args:
            obj: The object that generated the event.
            event: The event to filter.

        Returns:
            True if the event was consumed, False otherwise.
        """
        # --- Click trigger mode ---
        if self._trigger_mode == self.TriggerMode.CLICK:
            if self._trigger is not None and event.type() == QEvent.Type.MouseButtonRelease:
                if obj is self._trigger or self._is_child_of(obj, self._trigger):
                    if self._popup is not None and self._popup.isVisible():
                        self.hide_popup()
                    else:
                        self.show_popup()
                    return False

        # --- Hover trigger mode ---
        if self._trigger_mode == self.TriggerMode.HOVER:
            if self._trigger is not None:
                if event.type() == QEvent.Type.Enter:
                    if obj is self._trigger or self._is_child_of(obj, self._trigger):
                        if self._popup is None or not self._popup.isVisible():
                            self.show_popup()
                        return False
                if event.type() == QEvent.Type.Leave:
                    if obj is self._trigger or self._is_child_of(obj, self._trigger):
                        if not self._is_cursor_inside_popup():
                            self._fade_out()
                        return False

        # --- Focus trigger mode ---
        if self._trigger_mode == self.TriggerMode.FOCUS:
            if self._trigger is not None:
                if event.type() == QEvent.Type.FocusIn:
                    if obj is self._trigger or self._is_child_of(obj, self._trigger):
                        if self._popup is None or not self._popup.isVisible():
                            self.show_popup()
                        return False
                if event.type() == QEvent.Type.FocusOut:
                    if obj is self._trigger or self._is_child_of(obj, self._trigger):
                        self._fade_out()
                        return False

        # --- Outside click -> close popup (all non-manual modes) ---
        if (
            self._trigger_mode != self.TriggerMode.MANUAL
            and event.type() == QEvent.Type.MouseButtonPress
            and self._popup is not None
            and self._popup.isVisible()
        ):
            # Bug fix (66.12): use global cursor position to check if
            # click is inside popup geometry, not widget parent chain.
            if self._is_click_inside_popup(event):
                return False

            if self._is_child_of(obj, self._trigger) or obj is self._trigger:
                return False

            # Click is outside both popup and trigger — close
            self._fade_out()
            return False

        return super().eventFilter(obj, event)

    @staticmethod
    def _is_child_of(obj: Any, parent: QWidget | None) -> bool:
        """Check if obj is a descendant of parent widget.

        Args:
            obj: Object to check.
            parent: Potential ancestor widget.

        Returns:
            True if obj is inside the parent widget tree.
        """
        if parent is None or not isinstance(obj, QWidget):
            return False
        widget: QWidget | None = obj
        while widget is not None:
            if widget is parent:
                return True
            widget = widget.parentWidget()
        return False

    # -- Cleanup --

    def cleanup(self) -> None:
        """Disconnect signals and release resources."""
        if hasattr(self, "_reposition_timer"):
            self._reposition_timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self._destroy_popup()
        super().cleanup()

    # -- Private helpers --

    def _build_popup(self) -> QWidget:
        """Construct the popup widget with icon, title, and buttons.

        Stores references to the title label and buttons so that
        subsequent show_popup() calls can update text without rebuilding.
        """
        popup = QWidget(
            self.window(),
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint,
        )
        popup.setObjectName("popconfirm_popup")
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        root = QVBoxLayout(popup)
        root.setContentsMargins(4, 4, 4, 6)
        root.setSpacing(0)

        container = _PopconfirmContainer(popup)
        container.setObjectName("popconfirm_container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(12, 8, 12, 14)
        container_layout.setSpacing(8)

        # Row 1: icon + title
        header = QHBoxLayout()
        header.setSpacing(4)

        if self._show_icon:
            if self._custom_icon_widget is not None:
                self._custom_icon_widget.setParent(container)
                header.addWidget(self._custom_icon_widget)
            else:
                icon_label = QLabel(container)
                icon_label.setObjectName("popconfirm_icon")
                if self._icon is not None:
                    icon_label.setPixmap(self._icon.pixmap(QSize(16, 16)))
                else:
                    icon_label.setText("\u26a0")
                header.addWidget(icon_label)

        title_label = QLabel(self._title_text, container)
        title_label.setObjectName("popconfirm_title")
        title_label.setWordWrap(True)
        header.addWidget(title_label, 1)
        self._cached_title_label = title_label

        container_layout.addLayout(header)

        # Row 2: cancel + confirm buttons (with optional custom props)
        btn_row = QWidget(container)
        btn_row.setObjectName("popconfirm_btn_row")
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)
        btn_layout.addStretch()

        cancel_kwargs: dict[str, Any] = {
            "text": self._cancel_text,
            "button_type": TButton.ButtonType.DEFAULT,
            "size": TButton.ButtonSize.TINY,
            "parent": btn_row,
        }
        cancel_kwargs.update(self._negative_button_props)
        cancel_btn = TButton(**cancel_kwargs)
        cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(cancel_btn)
        self._cached_cancel_btn = cancel_btn

        confirm_kwargs: dict[str, Any] = {
            "text": self._confirm_text,
            "button_type": TButton.ButtonType.PRIMARY,
            "size": TButton.ButtonSize.TINY,
            "parent": btn_row,
        }
        confirm_kwargs.update(self._positive_button_props)
        confirm_btn = TButton(**confirm_kwargs)
        confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(confirm_btn)
        self._cached_confirm_btn = confirm_btn

        container_layout.addWidget(btn_row)
        root.addWidget(container)

        engine = ThemeEngine.instance()
        if engine.current_theme():
            try:
                qss = engine.render_qss("popconfirm.qss.j2")
                popup.setStyleSheet(qss)
            except Exception:
                pass

        # Pre-create the opacity effect and animation for reuse
        self._opacity_effect = QGraphicsOpacityEffect(popup)
        popup.setGraphicsEffect(self._opacity_effect)
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)

        popup.adjustSize()
        return popup

    def _position_popup(self) -> None:
        """Position the popup relative to the trigger based on placement."""
        if self._popup is None or self._trigger is None:
            return

        trigger_global = self._trigger.mapToGlobal(QPoint(0, 0))
        tw = self._trigger.width()
        th = self._trigger.height()
        pw = self._popup.width()
        ph = self._popup.height()
        margin = self._POPUP_MARGIN

        if self._placement == self.Placement.TOP:
            x = trigger_global.x() + (tw - pw) // 2
            y = trigger_global.y() - ph - margin
        elif self._placement == self.Placement.BOTTOM:
            x = trigger_global.x() + (tw - pw) // 2
            y = trigger_global.y() + th + margin
        elif self._placement == self.Placement.LEFT:
            x = trigger_global.x() - pw - margin
            y = trigger_global.y() + (th - ph) // 2
        else:  # RIGHT
            x = trigger_global.x() + tw + margin
            y = trigger_global.y() + (th - ph) // 2

        self._popup.move(x, y)

    def _reposition_popup_tick(self) -> None:
        """Reposition the popup to stay anchored to the trigger."""
        if self._popup is None or self._trigger is None:
            if hasattr(self, "_reposition_timer"):
                self._reposition_timer.stop()
            return
        self._position_popup()

    def _fade_in(self) -> None:
        """Animate popup fade-in over 150ms, reusing cached effect."""
        if self._popup is None or self._opacity_effect is None:
            return

        # Stop any running animation before starting a new one
        if self._fade_anim is not None:
            self._fade_anim.stop()
            if self._fade_anim_connected:
                self._fade_anim.finished.disconnect()
                self._fade_anim_connected = False

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(150)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()

    def _fade_out(self) -> None:
        """Animate popup fade-out over 150ms, then hide."""
        if self._popup is None or self._opacity_effect is None:
            return

        # Stop any running animation before starting a new one
        if self._fade_anim is not None:
            self._fade_anim.stop()
            if self._fade_anim_connected:
                self._fade_anim.finished.disconnect()
                self._fade_anim_connected = False

        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(150)
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.finished.connect(self.hide_popup)
        self._fade_anim_connected = True
        self._fade_anim.start()

    def _on_confirm(self) -> None:
        """Handle confirm button click."""
        self.hide_popup()
        if self._on_positive_click is not None:
            self._on_positive_click()
        self.confirmed.emit()
        self._emit_bus_event("confirmed")

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.hide_popup()
        if self._on_negative_click is not None:
            self._on_negative_click()
        self.cancelled.emit()
        self._emit_bus_event("cancelled")

    def _is_child_of_popup(self, obj: Any) -> bool:
        """Check if obj is a descendant of the popup widget.

        Args:
            obj: Object to check.

        Returns:
            True if obj is inside the popup widget tree.
        """
        if self._popup is None or not isinstance(obj, QWidget):
            return False
        widget: QWidget | None = obj
        while widget is not None:
            if widget is self._popup:
                return True
            widget = widget.parentWidget()
        return False

    def _is_click_inside_popup(self, event: QEvent) -> bool:
        """Check if a mouse press event occurred inside the popup geometry.

        Uses global cursor position to reliably detect clicks inside the
        popup window, even on non-widget areas (translucent background).

        Args:
            event: The mouse press event.

        Returns:
            True if the click is inside the popup.
        """
        if self._popup is None:
            return False

        global_pos: QPoint | None = None
        if isinstance(event, QMouseEvent):
            global_pos = event.globalPosition().toPoint()

        if global_pos is None:
            global_pos = QCursor.pos()

        popup_rect = QRect(self._popup.mapToGlobal(QPoint(0, 0)), self._popup.size())
        return popup_rect.contains(global_pos)

    def _is_cursor_inside_popup(self) -> bool:
        """Check if the cursor is currently inside the popup geometry.

        Returns:
            True if the cursor is over the popup.
        """
        if self._popup is None:
            return False
        popup_rect = QRect(self._popup.mapToGlobal(QPoint(0, 0)), self._popup.size())
        return popup_rect.contains(QCursor.pos())
