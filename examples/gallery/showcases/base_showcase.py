"""BaseShowcase: base class for all component showcase panels.

Provides ``add_section`` to build titled, described content blocks and
a ``hbox`` static helper for horizontal widget layouts.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from examples.gallery.styles.gallery_styles import GalleryStyles
from tyto_ui_lib import ThemeEngine


class BaseShowcase(QWidget):
    """Base class for component showcases.

    Subclasses add sections via ``add_section`` in their ``__init__``.
    Each section consists of a title, description, and a content widget.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(16)

        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._refresh_styles)

    def add_section(self, title: str, description: str, content: QWidget) -> None:
        """Add a showcase section with title, description, and content widget.

        Args:
            title: Section heading text.
            description: Brief explanation of what the section demonstrates.
            content: Widget containing the component examples.
        """
        title_label = QLabel(title)
        title_label.setProperty("class", "showcase_title")
        title_label.setStyleSheet(GalleryStyles.showcase_section_title_style())
        self._layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setProperty("class", "showcase_desc")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(GalleryStyles.showcase_section_desc_style())
        self._layout.addWidget(desc_label)

        self._layout.addWidget(content)

    @staticmethod
    def hbox(*widgets: QWidget) -> QWidget:
        """Wrap widgets in a horizontal layout container.

        Args:
            widgets: Widgets to arrange horizontally.

        Returns:
            A container QWidget with horizontal layout.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        for w in widgets:
            layout.addWidget(w)
        layout.addStretch()
        return container

    def _refresh_styles(self, _theme: str) -> None:
        """Refresh section label styles on theme change."""
        for i in range(self._layout.count()):
            item = self._layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if w.property("class") == "showcase_title":
                    w.setStyleSheet(GalleryStyles.showcase_section_title_style())
                elif w.property("class") == "showcase_desc":
                    w.setStyleSheet(GalleryStyles.showcase_section_desc_style())
