"""Empty state placeholder component.

Displays a vertically centered layout of icon, description text, and
optional extra content when no data is available.
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine

# Default SVG icon for empty state (simple illustration).
_DEFAULT_EMPTY_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" fill="none">
  <rect x="20" y="30" width="56" height="40" rx="4"
        stroke="#c2c2c2" stroke-width="2" fill="#f5f5f5"/>
  <line x1="30" y1="45" x2="66" y2="45" stroke="#d9d9d9" stroke-width="2"/>
  <line x1="30" y1="55" x2="56" y2="55" stroke="#d9d9d9" stroke-width="2"/>
  <circle cx="48" cy="78" r="4" fill="#d9d9d9"/>
</svg>"""

# Size-to-image-size mapping for EmptySize variants.
_SIZE_IMAGE_MAP: dict[str, int] = {
    "tiny": 48,
    "small": 64,
    "medium": 96,
    "large": 128,
    "huge": 192,
}


class TEmpty(BaseWidget):
    """Empty state placeholder with customizable icon, text, and action area.

    Displays a centered layout of icon, description text, and optional
    extra content when no data is available.

    Args:
        description: Text displayed below the icon.
        image: Custom icon (QIcon or QPixmap) replacing the default SVG.
        image_size: Explicit size in pixels for the icon area. Overrides size enum.
        size: Size variant controlling the icon area dimensions.
        show_description: Whether to display the description text.
        show_icon: Whether to display the icon area.
        parent: Optional parent widget.

    Example:
        >>> empty = TEmpty(description="No results found")
        >>> empty.set_extra(TButton(text="Refresh"))
    """

    class EmptySize(str, Enum):
        """Size variants for the empty state component."""

        TINY = "tiny"
        SMALL = "small"
        MEDIUM = "medium"
        LARGE = "large"
        HUGE = "huge"

    def __init__(
        self,
        description: str = "暂无数据",
        image: QIcon | QPixmap | None = None,
        image_size: int | None = None,
        size: EmptySize = EmptySize.MEDIUM,
        show_description: bool = True,
        show_icon: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        self._description_text = description
        self._image = image
        self._size = size
        self._image_size = image_size if image_size is not None else _SIZE_IMAGE_MAP[size.value]
        self._show_description = show_description
        self._show_icon = show_icon
        self._extra_widget: QWidget | None = None

        super().__init__(parent)
        self._build_ui()
        self._apply_size_property()

    # -- Public API -----------------------------------------------------------

    @property
    def description(self) -> str:
        """Return the current description text."""
        return self._description_text

    def set_description(self, description: str) -> None:
        """Update the description text.

        Args:
            description: New description string.
        """
        self._description_text = description
        self._desc_label.setText(description)

    @property
    def size(self) -> EmptySize:
        """Return the current size variant."""
        return self._size

    def set_size(self, size: EmptySize) -> None:
        """Update the size variant.

        Args:
            size: New size variant.
        """
        self._size = size
        self._image_size = _SIZE_IMAGE_MAP[size.value]
        self._icon_container.setFixedSize(self._image_size, self._image_size)
        self._update_icon()
        self._apply_size_property()

    @property
    def show_description(self) -> bool:
        """Return whether the description text is visible."""
        return self._show_description

    def set_show_description(self, visible: bool) -> None:
        """Control visibility of the description text area.

        Args:
            visible: True to show, False to hide.
        """
        self._show_description = visible
        self._desc_label.setVisible(visible)

    @property
    def show_icon(self) -> bool:
        """Return whether the icon area is visible."""
        return self._show_icon

    def set_show_icon(self, visible: bool) -> None:
        """Control visibility of the icon area.

        Args:
            visible: True to show, False to hide.
        """
        self._show_icon = visible
        self._icon_container.setVisible(visible)

    def set_image(self, image: QIcon | QPixmap | None) -> None:
        """Replace the displayed icon.

        Args:
            image: A QIcon, QPixmap, or None to restore the default SVG.
        """
        self._image = image
        self._update_icon()

    @property
    def image_size(self) -> int:
        """Return the current icon area size in pixels."""
        return self._image_size

    def set_extra(self, widget: QWidget) -> None:
        """Set a custom action area below the description.

        Any previously set extra widget is removed.

        Args:
            widget: Widget to embed as the action area.
        """
        if self._extra_widget is not None:
            self._layout.removeWidget(self._extra_widget)
            self._extra_widget.setParent(None)  # type: ignore[call-overload]

        self._extra_widget = widget
        self._layout.addWidget(widget, 0, Qt.AlignmentFlag.AlignHCenter)

    # -- Private helpers ------------------------------------------------------

    def _apply_size_property(self) -> None:
        """Set the QSS dynamic property for size variant styling."""
        self.setProperty("emptySize", self._size.value)
        self.style().unpolish(self)
        self.style().polish(self)

    def _build_ui(self) -> None:
        """Construct the vertically centered layout."""
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.setSpacing(12)

        # Icon area
        self._icon_container = QWidget(self)
        self._icon_container.setObjectName("empty_icon")
        self._icon_container.setFixedSize(self._image_size, self._image_size)
        icon_layout = QVBoxLayout(self._icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._svg_widget: QSvgWidget | None = None
        self._pixmap_label: QLabel | None = None
        self._update_icon()

        self._layout.addWidget(self._icon_container, 0, Qt.AlignmentFlag.AlignHCenter)
        self._icon_container.setVisible(self._show_icon)

        # Description label
        self._desc_label = QLabel(self._description_text, self)
        self._desc_label.setObjectName("empty_description")
        self._desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._desc_label.setWordWrap(True)
        self._layout.addWidget(self._desc_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self._desc_label.setVisible(self._show_description)

    def _update_icon(self) -> None:
        """Refresh the icon display based on current image setting."""
        container_layout = self._icon_container.layout()
        if container_layout is not None:
            if self._svg_widget is not None:
                container_layout.removeWidget(self._svg_widget)
                self._svg_widget.deleteLater()
                self._svg_widget = None
            if self._pixmap_label is not None:
                container_layout.removeWidget(self._pixmap_label)
                self._pixmap_label.deleteLater()
                self._pixmap_label = None

        if self._image is None:
            self._svg_widget = QSvgWidget(self._icon_container)
            self._svg_widget.load(bytearray(_DEFAULT_EMPTY_SVG.encode("utf-8")))
            self._svg_widget.setFixedSize(self._image_size, self._image_size)
            if container_layout is not None:
                container_layout.addWidget(self._svg_widget)
        else:
            self._pixmap_label = QLabel(self._icon_container)
            self._pixmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if isinstance(self._image, QIcon):
                pm = self._image.pixmap(self._image_size, self._image_size)
            else:
                pm = self._image.scaled(
                    self._image_size,
                    self._image_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            self._pixmap_label.setPixmap(pm)
            if container_layout is not None:
                container_layout.addWidget(self._pixmap_label)

    def apply_theme(self) -> None:
        """Update styles from current theme tokens."""
        engine = ThemeEngine.instance()
        try:
            qss = engine.render_qss("empty.qss.j2")
            self.setStyleSheet(qss)
        except RuntimeError:
            pass
