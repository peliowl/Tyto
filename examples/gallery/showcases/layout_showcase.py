"""LayoutShowcase: demonstrates TLayout with header, sider, content, footer."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TLayout, TLayoutContent, TLayoutFooter, TLayoutHeader, TLayoutSider


class LayoutShowcase(BaseShowcase):
    """Showcase for the TLayout organism component.

    Sections: basic layout, layout with sider.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic layout: header + content + footer
        layout1 = TLayout()
        layout1.setFixedHeight(300)

        header = TLayoutHeader(height=50)
        header.set_content(QLabel("Header"))
        layout1.add_header(header)

        content = TLayoutContent()
        content.set_content(QLabel("Main Content Area"))
        layout1.add_content(content)

        footer = TLayoutFooter(height=40)
        footer.set_content(QLabel("Footer"))
        layout1.add_footer(footer)

        self.add_section(
            "Basic Layout",
            "Header, content, and footer structure.",
            layout1,
        )

        # Layout with sider
        layout2 = TLayout()
        layout2.setFixedHeight(300)

        header2 = TLayoutHeader(height=50)
        header2.set_content(QLabel("Header"))
        layout2.add_header(header2)

        sider = TLayoutSider(width=180, collapsed_width=60)
        sider.set_content(QLabel("Sider"))
        layout2.add_sider(sider)

        content2 = TLayoutContent()
        content2.set_content(QLabel("Content with Sider"))
        layout2.add_content(content2)

        self.add_section(
            "With Sider",
            "Layout with a collapsible sidebar.",
            layout2,
        )
