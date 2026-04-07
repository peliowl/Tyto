"""TModal organism component: modal dialog with mask overlay.

Provides a centred dialog with semi-transparent mask, scale-in animation,
customisable title/content/footer areas, and closable/mask_closable controls.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


class _MaskWidget(QWidget):
    """Semi-transparent overlay that captures clicks outside the dialog."""

    mask_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("modal_mask")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Emit mask_clicked when the mask area is pressed."""
        self.mask_clicked.emit()
        event.accept()


class TModal(BaseWidget):
    """Modal dialog component with mask overlay and scale animation.

    Displays a centred dialog over a semi-transparent mask that blocks
    interaction with the underlying UI.  Supports customisable title,
    body content, and footer areas.

    Args:
        title: Dialog title text.
        closable: Whether to show the close button and allow mask close.
        mask_closable: Whether clicking the mask closes the dialog.
        parent: Optional parent widget.

    Signals:
        closed: Emitted when the modal is closed (by button or mask click).

    Example:
        >>> modal = TModal(title="Confirm", parent=window)
        >>> modal.set_content(QLabel("Are you sure?"))
        >>> modal.open()
    """

    closed = Signal()

    def __init__(
        self,
        title: str = "",
        closable: bool = True,
        mask_closable: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._title_text = title
        self._closable = closable
        self._mask_closable = mask_closable

        # Full-screen overlay
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        # Root layout fills the entire widget
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Mask background
        self._mask = _MaskWidget(self)
        self._mask.mask_clicked.connect(self._on_mask_clicked)
        root_layout.addWidget(self._mask)

        # Mask layout centres the dialog
        mask_layout = QVBoxLayout(self._mask)
        mask_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dialog container
        self._dialog = QWidget(self._mask)
        self._dialog.setObjectName("modal_dialog")
        self._dialog.setMinimumSize(QSize(400, 200))
        self._dialog.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        mask_layout.addWidget(self._dialog)

        dialog_layout = QVBoxLayout(self._dialog)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.setSpacing(0)

        # -- Header: [title] [close_btn?] --
        self._header = QWidget(self._dialog)
        self._header.setObjectName("modal_header")
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self._title_label = QLabel(title, self._header)
        self._title_label.setObjectName("modal_title")
        header_layout.addWidget(self._title_label, 1)

        self._close_btn: QPushButton | None = None
        if closable:
            self._close_btn = QPushButton("\u2715", self._header)
            self._close_btn.setObjectName("modal_close_btn")
            self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_btn.clicked.connect(self.close)
            header_layout.addWidget(self._close_btn)

        dialog_layout.addWidget(self._header)

        # -- Body --
        self._body = QWidget(self._dialog)
        self._body.setObjectName("modal_body")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(self._body, 1)

        # -- Footer --
        self._footer = QWidget(self._dialog)
        self._footer.setObjectName("modal_footer")
        self._footer_layout = QHBoxLayout(self._footer)
        self._footer_layout.setContentsMargins(0, 0, 0, 0)
        self._footer.setVisible(False)
        dialog_layout.addWidget(self._footer)

        self.hide()
        self.apply_theme()

    # -- Public API --

    @property
    def closable(self) -> bool:
        """Return whether the modal has a close button."""
        return self._closable

    @property
    def mask_closable(self) -> bool:
        """Return whether clicking the mask closes the modal."""
        return self._mask_closable

    @property
    def title_text(self) -> str:
        """Return the modal title string."""
        return self._title_text

    def set_content(self, widget: QWidget) -> None:
        """Set the main body content widget.

        Args:
            widget: Widget to display in the body area.
        """
        # Clear existing content
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._body_layout.addWidget(widget)

    def set_footer(self, widget: QWidget) -> None:
        """Set the footer area widget (typically buttons).

        Args:
            widget: Widget to display in the footer area.
        """
        while self._footer_layout.count():
            item = self._footer_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._footer_layout.addWidget(widget)
        self._footer.setVisible(True)

    def open(self) -> None:
        """Show the modal with a scale-in animation."""
        # Resize to parent or screen
        parent = self.parentWidget()
        if parent is not None:
            self.resize(parent.size())
        self.show()
        self.raise_()

        # Scale-in animation on the dialog
        self._dialog.setGraphicsEffect(None)
        anim = QPropertyAnimation(self._dialog, b"size", self)
        target_size = self._dialog.sizeHint()
        anim.setDuration(200)
        anim.setStartValue(QSize(int(target_size.width() * 0.8), int(target_size.height() * 0.8)))
        anim.setEndValue(target_size)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

    def close(self) -> None:
        """Close the modal with animation and emit ``closed``."""
        anim = QPropertyAnimation(self._dialog, b"size", self)
        target_size = self._dialog.size()
        anim.setDuration(150)
        anim.setStartValue(target_size)
        anim.setEndValue(QSize(int(target_size.width() * 0.8), int(target_size.height() * 0.8)))
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self._on_close_finished)
        anim.start()

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this modal."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("modal.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    # -- Private --

    def _on_mask_clicked(self) -> None:
        """Handle mask click: close if mask_closable and closable."""
        if self._closable and self._mask_closable:
            self.close()

    def _on_close_finished(self) -> None:
        """Handle close animation completion."""
        self.hide()
        self.closed.emit()
