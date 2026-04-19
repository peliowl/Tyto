"""TAlert molecule component: non-floating alert banner with semantic types.

Provides a persistent, inline alert with default/success/info/warning/error
types, optional title, description, close button with fade-out animation,
action slot, custom icon support, and a left-side colored border accent.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.utils.color import parse_color

_ICONS: dict[str, str] = {
    "default": "ℹ",
    "success": "✔",
    "info": "ℹ",
    "warning": "⚠",
    "error": "✖",
}


class TAlert(BaseWidget):
    """Non-floating alert banner component with semantic types.

    Displays a persistent, inline alert with an icon, optional title,
    description text, close button, and action slot.

    Args:
        alert_type: Semantic type (default/success/info/warning/error).
        title: Optional title text displayed in bold.
        description: Optional description text below the title.
        closable: Whether to show a close button.
        bordered: Whether to show a left-side colored border accent.
        show_icon: Whether to show the type icon. Defaults to True.
        parent: Optional parent widget.

    Signals:
        closed: Emitted when the alert is closed via the close button.

    Example:
        >>> alert = TAlert(
        ...     alert_type=TAlert.AlertType.SUCCESS,
        ...     title="Success",
        ...     description="Operation completed.",
        ...     closable=True,
        ... )
        >>> alert.closed.connect(lambda: print("Alert closed"))
    """

    class AlertType(str, Enum):
        """Semantic alert types."""

        DEFAULT = "default"
        SUCCESS = "success"
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"

    closed = Signal()
    after_leave = Signal()

    def __init__(
        self,
        alert_type: AlertType = AlertType.INFO,
        title: str = "",
        description: str = "",
        closable: bool = False,
        bordered: bool = True,
        show_icon: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        self._alert_type = alert_type
        self._title_text = title
        self._description_text = description
        self._closable = closable
        self._bordered = bordered
        self._show_icon = show_icon
        self._action_widget: QWidget | None = None
        self._custom_icon: QWidget | None = None

        super().__init__(parent)

        self.setProperty("alertType", alert_type.value)
        self.setProperty("bordered", str(bordered).lower())

        # Root layout: horizontal [icon | content | close_btn]
        self._root_layout = QHBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        # Icon
        self._icon_label = QLabel(_ICONS.get(alert_type.value, "ℹ"), self)
        self._icon_label.setObjectName("alert_icon")
        self._icon_label.setVisible(show_icon)
        self._root_layout.addWidget(self._icon_label)

        # Content column: title, description, action
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(2)

        if title:
            self._title_label = QLabel(title, self)
            self._title_label.setObjectName("alert_title")
            self._title_label.setWordWrap(True)
            self._content_layout.addWidget(self._title_label)
        else:
            self._title_label = None

        if description:
            self._desc_label = QLabel(description, self)
            self._desc_label.setObjectName("alert_description")
            self._desc_label.setWordWrap(True)
            self._content_layout.addWidget(self._desc_label)
        else:
            self._desc_label = None

        # Placeholder for action widget
        self._action_placeholder = QVBoxLayout()
        self._action_placeholder.setContentsMargins(0, 4, 0, 0)
        self._content_layout.addLayout(self._action_placeholder)

        self._root_layout.addLayout(self._content_layout, 1)

        # Close button
        self._close_btn: QToolButton | None = None
        if closable:
            self._close_btn = QToolButton(self)
            self._close_btn.setObjectName("alert_close_btn")
            self._close_btn.setText("✕")
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self._on_close_clicked)
            self._root_layout.addWidget(self._close_btn)

        self.apply_theme()

    # -- Public API --

    @property
    def alert_type(self) -> AlertType:
        """Return the semantic alert type.

        Returns:
            The current AlertType value.
        """
        return self._alert_type

    @property
    def title(self) -> str:
        """Return the title text.

        Returns:
            The title string.
        """
        return self._title_text

    @property
    def description(self) -> str:
        """Return the description text.

        Returns:
            The description string.
        """
        return self._description_text

    @property
    def closable(self) -> bool:
        """Return whether the alert is closable.

        Returns:
            True if the close button is shown.
        """
        return self._closable

    @property
    def show_icon(self) -> bool:
        """Return whether the type icon is visible.

        Returns:
            True if the icon is shown.
        """
        return self._show_icon

    @show_icon.setter
    def show_icon(self, value: bool) -> None:
        """Set icon visibility.

        Args:
            value: Whether to show the type icon.
        """
        self._show_icon = value
        self._icon_label.setVisible(value and self._custom_icon is None)
        if self._custom_icon is not None:
            self._custom_icon.setVisible(value)

    def set_icon(self, widget: QWidget) -> None:
        """Replace the default type icon with a custom widget.

        Args:
            widget: Custom icon widget to display instead of the default.
        """
        # Remove previous custom icon if any
        if self._custom_icon is not None:
            self._root_layout.removeWidget(self._custom_icon)
            self._custom_icon.setParent(None)  # type: ignore[call-overload]

        self._custom_icon = widget
        # Hide the default label icon
        self._icon_label.setVisible(False)
        # Propagate objectName so QSS rules (font-size, padding) apply
        widget.setObjectName("alert_icon")
        # Insert custom icon at position 0 (before content)
        self._root_layout.insertWidget(0, widget)
        widget.setVisible(self._show_icon)

    def set_alert_type(self, alert_type: AlertType) -> None:
        """Set the semantic alert type and refresh styles.

        Args:
            alert_type: New alert type.
        """
        self._alert_type = alert_type
        self.setProperty("alertType", alert_type.value)
        self._icon_label.setText(_ICONS.get(alert_type.value, "ℹ"))
        self.style().unpolish(self)
        self.style().polish(self)

    def set_title(self, title: str) -> None:
        """Set the title text.

        Args:
            title: New title string.
        """
        self._title_text = title
        if self._title_label is not None:
            self._title_label.setText(title)
            self._title_label.setVisible(bool(title))
        elif title:
            self._title_label = QLabel(title, self)
            self._title_label.setObjectName("alert_title")
            self._title_label.setWordWrap(True)
            self._content_layout.insertWidget(0, self._title_label)

    def set_description(self, description: str) -> None:
        """Set the description text.

        Args:
            description: New description string.
        """
        self._description_text = description
        if self._desc_label is not None:
            self._desc_label.setText(description)
            self._desc_label.setVisible(bool(description))
        elif description:
            idx = 1 if self._title_label is not None else 0
            self._desc_label = QLabel(description, self)
            self._desc_label.setObjectName("alert_description")
            self._desc_label.setWordWrap(True)
            self._content_layout.insertWidget(idx, self._desc_label)

    def set_closable(self, closable: bool) -> None:
        """Set whether the alert shows a close button.

        Args:
            closable: True to show close button.
        """
        self._closable = closable
        if closable and self._close_btn is None:
            self._close_btn = QToolButton(self)
            self._close_btn.setObjectName("alert_close_btn")
            self._close_btn.setText("✕")
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self._on_close_clicked)
            self._root_layout.addWidget(self._close_btn)
        elif not closable and self._close_btn is not None:
            self._root_layout.removeWidget(self._close_btn)
            self._close_btn.deleteLater()
            self._close_btn = None

    @property
    def bordered(self) -> bool:
        """Return whether the left border accent is shown.

        Returns:
            True if bordered.
        """
        return self._bordered

    @bordered.setter
    def bordered(self, value: bool) -> None:
        """Set the bordered state and refresh styles.

        Args:
            value: Whether to show the left border accent.
        """
        self._bordered = value
        self.setProperty("bordered", str(value).lower())
        self.style().unpolish(self)
        self.style().polish(self)

    def set_action(self, widget: QWidget) -> None:
        """Embed an action widget below the description text.

        Args:
            widget: The widget to embed (e.g. a TButton).
        """
        if self._action_widget is not None:
            self._action_placeholder.removeWidget(self._action_widget)
            self._action_widget.setParent(None)  # type: ignore[call-overload]
        self._action_widget = widget
        self._action_placeholder.addWidget(widget)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this alert."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("alert.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    # -- Paint left accent bar --

    def paintEvent(self, event: object) -> None:  # noqa: N802
        """Paint the left accent bar when bordered is True."""
        # Let QSS paint the base styles first
        super().paintEvent(event)  # type: ignore[arg-type]

        if not self._bordered:
            return

        # Get the accent color for the current alert type
        color_key = {
            self.AlertType.DEFAULT: "info",
            self.AlertType.SUCCESS: "success",
            self.AlertType.INFO: "info",
            self.AlertType.WARNING: "warning",
            self.AlertType.ERROR: "error",
        }.get(self._alert_type, "info")

        try:
            engine = ThemeEngine.instance()
            accent = parse_color(str(engine.get_token("colors", color_key)))
            radius = int(engine.get_token("radius", "medium"))
        except Exception:
            accent = QColor("#2080f0")
            radius = 4

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(accent)

        # Draw the left accent bar as a simple rectangle
        bar_width = 3.0
        painter.drawRoundedRect(
            QRectF(0, 1, bar_width, self.height() - 2),
            1, 1,
        )

        painter.end()

    # -- Size hint --

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(400, 80)

    # -- Private --

    def _on_close_clicked(self) -> None:
        """Handle close button click: fade out then hide and emit closed."""
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(200)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(self._on_fade_finished)
        anim.start()

    def _on_fade_finished(self) -> None:
        """Called when fade-out animation completes."""
        self.setVisible(False)
        self.closed.emit()
        self._emit_bus_event("closed")
        self.after_leave.emit()
        self._emit_bus_event("after_leave")
