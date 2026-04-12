"""TCard organism component: card container with header, body, and footer.

Provides a standard content container with optional title, header extras,
closable behaviour, size variants controlling padding, and hoverable shadow
deepening effect.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


# Padding values per card size (px).
_SIZE_PADDING: dict[str, int] = {
    "small": 12,
    "medium": 20,
    "large": 24,
}


class TCard(BaseWidget, HoverEffectMixin):
    """Card container with header, body, and footer sections.

    Supports hover shadow deepening effect and closable behaviour.
    The card provides three areas: a header with title and optional extra
    widget, a body for main content, and an optional footer.

    Args:
        title: Header title text.
        size: Card size controlling internal padding.
        hoverable: Whether to deepen shadow on hover.
        bordered: Whether to display a border.
        closable: Whether to show a close button in the header.
        parent: Optional parent widget.

    Signals:
        closed: Emitted when the close button is clicked.

    Example:
        >>> card = TCard(title="My Card", size=TCard.CardSize.MEDIUM)
        >>> card.set_content(QLabel("Hello"))
        >>> card.set_footer(QLabel("Footer info"))
    """

    class CardSize(str, Enum):
        """Card size variants controlling internal padding."""

        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"

    closed = Signal()

    def __init__(
        self,
        title: str = "",
        size: CardSize = CardSize.MEDIUM,
        hoverable: bool = False,
        bordered: bool = True,
        closable: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._init_hover_effect()

        self._title_text = title
        self._size = size
        self._hoverable = hoverable
        self._bordered = bordered
        self._closable = closable

        # Shadow effect for hoverable cards
        self._shadow: QGraphicsDropShadowEffect | None = None
        self._shadow_anim: QPropertyAnimation | None = None

        # Set QSS dynamic properties
        self.setProperty("cardSize", size.value)
        self.setProperty("bordered", str(bordered).lower())

        self._build_ui()
        self._setup_shadow()
        self.apply_theme()

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct the header / body / footer layout."""
        pad = _SIZE_PADDING.get(self._size.value, 20)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # -- Header -----------------------------------------------------------
        self._header = QWidget(self)
        self._header.setObjectName("card_header")
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(pad, pad, pad, 0)
        header_layout.setSpacing(0)

        self._title_label = QLabel(self._title_text, self._header)
        self._title_label.setObjectName("card_title")
        header_layout.addWidget(self._title_label, 1)

        # Placeholder for header extra widget
        self._header_extra_container = QWidget(self._header)
        self._header_extra_layout = QHBoxLayout(self._header_extra_container)
        self._header_extra_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self._header_extra_container)

        # Close button
        self._close_btn: QPushButton | None = None
        if self._closable:
            self._close_btn = QPushButton("\u2715", self._header)
            self._close_btn.setObjectName("card_close_btn")
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self._on_close_clicked)
            header_layout.addWidget(self._close_btn)

        # Hide header if no title, no closable, and no extra
        if not self._title_text and not self._closable:
            self._header.setVisible(False)

        root.addWidget(self._header)

        # -- Body -------------------------------------------------------------
        self._body = QWidget(self)
        self._body.setObjectName("card_body")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(pad, pad, pad, pad)
        self._body_layout.setSpacing(0)
        root.addWidget(self._body, 1)

        # -- Footer -----------------------------------------------------------
        self._footer = QWidget(self)
        self._footer.setObjectName("card_footer")
        self._footer_layout = QVBoxLayout(self._footer)
        self._footer_layout.setContentsMargins(pad, pad, pad, pad)
        self._footer_layout.setSpacing(0)
        self._footer.setVisible(False)
        root.addWidget(self._footer)

    def _setup_shadow(self) -> None:
        """Initialise the drop-shadow effect for hoverable cards."""
        if not self._hoverable:
            return

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 2)
        self._shadow.setColor(Qt.GlobalColor.black)
        # Start with small shadow (blur radius 8)
        self._shadow.setBlurRadius(8)
        self.setGraphicsEffect(self._shadow)

    # -- Public API -----------------------------------------------------------

    @property
    def title_text(self) -> str:
        """Return the card title string."""
        return self._title_text

    @property
    def size(self) -> CardSize:
        """Return the card size variant."""
        return self._size

    @property
    def hoverable(self) -> bool:
        """Return whether the card has hover shadow effect."""
        return self._hoverable

    @property
    def bordered(self) -> bool:
        """Return whether the card displays a border."""
        return self._bordered

    @property
    def closable(self) -> bool:
        """Return whether the card has a close button."""
        return self._closable

    def set_header_extra(self, widget: QWidget) -> None:
        """Set a widget in the header's right side (before close button).

        Args:
            widget: Widget to embed in the header extra area.
        """
        # Clear existing extra content
        while self._header_extra_layout.count():
            item = self._header_extra_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._header_extra_layout.addWidget(widget)
        # Ensure header is visible when extra is set
        self._header.setVisible(True)

    def set_content(self, widget: QWidget) -> None:
        """Set the body area content widget.

        Args:
            widget: Widget to display in the body area.
        """
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._body_layout.addWidget(widget)

    def set_footer(self, widget: QWidget) -> None:
        """Set the footer area content widget.

        Args:
            widget: Widget to display in the footer area.
        """
        while self._footer_layout.count():
            item = self._footer_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._footer_layout.addWidget(widget)
        self._footer.setVisible(True)

    # -- Theme ----------------------------------------------------------------

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this card."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("card.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    # -- Hover shadow ---------------------------------------------------------

    def enterEvent(self, event: object) -> None:  # type: ignore[override]
        """Deepen shadow on hover for hoverable cards."""
        if self._hoverable and self._shadow is not None:
            self._animate_shadow(16)  # shadows.medium blur
        super().enterEvent(event)  # type: ignore[arg-type]

    def leaveEvent(self, event: object) -> None:  # type: ignore[override]
        """Restore shadow on leave for hoverable cards."""
        if self._hoverable and self._shadow is not None:
            self._animate_shadow(8)  # shadows.small blur
        super().leaveEvent(event)  # type: ignore[arg-type]

    def _animate_shadow(self, target_blur: int) -> None:
        """Animate the shadow blur radius to *target_blur*.

        Args:
            target_blur: Target blur radius value.
        """
        if self._shadow is None:
            return

        if self._shadow_anim is not None:
            self._shadow_anim.stop()

        self._shadow_anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._shadow_anim.setDuration(200)
        self._shadow_anim.setStartValue(self._shadow.blurRadius())
        self._shadow_anim.setEndValue(target_blur)
        self._shadow_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._shadow_anim.start()

    # -- Private --------------------------------------------------------------

    def _on_close_clicked(self) -> None:
        """Handle close button click: emit closed signal."""
        self.closed.emit()
