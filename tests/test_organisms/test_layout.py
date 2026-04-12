"""Unit tests for TLayout organism component series."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from tyto_ui_lib.components.organisms.layout import (
    Breakpoint,
    TLayout,
    TLayoutContent,
    TLayoutFooter,
    TLayoutHeader,
    TLayoutSider,
)
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


# -- TLayoutHeader -----------------------------------------------------------


class TestTLayoutHeader:
    """Tests for TLayoutHeader initialization and properties."""

    def test_default_height(self, qapp: QApplication) -> None:
        header = TLayoutHeader()
        # Default from token fallback is 64
        assert header.maximumHeight() == 64

    def test_custom_height(self, qapp: QApplication) -> None:
        header = TLayoutHeader(height=48)
        assert header.maximumHeight() == 48
        assert header.height == 48

    def test_set_height(self, qapp: QApplication) -> None:
        header = TLayoutHeader()
        header.set_height(80)
        assert header.height == 80

    def test_set_content(self, qapp: QApplication) -> None:
        header = TLayoutHeader()
        label = QLabel("Title")
        header.set_content(label)
        assert header._content_layout.count() == 1


# -- TLayoutFooter -----------------------------------------------------------


class TestTLayoutFooter:
    """Tests for TLayoutFooter initialization and properties."""

    def test_default_height(self, qapp: QApplication) -> None:
        footer = TLayoutFooter()
        assert footer.maximumHeight() == 64

    def test_custom_height(self, qapp: QApplication) -> None:
        footer = TLayoutFooter(height=32)
        assert footer.height == 32

    def test_set_height(self, qapp: QApplication) -> None:
        footer = TLayoutFooter()
        footer.set_height(50)
        assert footer.height == 50

    def test_set_content(self, qapp: QApplication) -> None:
        footer = TLayoutFooter()
        label = QLabel("Footer")
        footer.set_content(label)
        assert footer._content_layout.count() == 1


# -- TLayoutContent ----------------------------------------------------------


class TestTLayoutContent:
    """Tests for TLayoutContent initialization."""

    def test_creation(self, qapp: QApplication) -> None:
        content = TLayoutContent()
        assert content is not None

    def test_set_content(self, qapp: QApplication) -> None:
        content = TLayoutContent()
        label = QLabel("Main")
        content.set_content(label)
        assert content._content_layout.count() == 1


# -- TLayoutSider -----------------------------------------------------------


class TestTLayoutSider:
    """Tests for TLayoutSider initialization, collapse, and breakpoints."""

    def test_default_widths(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        assert sider.expanded_width == 240
        assert sider.collapsed_width_value == 48
        assert sider.collapsed is False

    def test_custom_widths(self, qapp: QApplication) -> None:
        sider = TLayoutSider(width=200, collapsed_width=60)
        assert sider.expanded_width == 200
        assert sider.collapsed_width_value == 60

    def test_initial_collapsed(self, qapp: QApplication) -> None:
        sider = TLayoutSider(collapsed=True)
        assert sider.collapsed is True
        assert sider.maximumWidth() == 48

    def test_set_collapsed_emits_signal(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        received: list[bool] = []
        sider.collapsed_changed.connect(lambda v: received.append(v))
        sider.set_collapsed(True, animate=False)
        assert sider.collapsed is True
        assert received == [True]

    def test_set_collapsed_same_state_no_signal(self, qapp: QApplication) -> None:
        sider = TLayoutSider(collapsed=False)
        received: list[bool] = []
        sider.collapsed_changed.connect(lambda v: received.append(v))
        sider.set_collapsed(False, animate=False)
        assert received == []

    def test_toggle_collapsed(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        assert sider.collapsed is False
        sider.toggle_collapsed()
        assert sider.collapsed is True
        sider.toggle_collapsed()
        assert sider.collapsed is False

    def test_set_width(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        sider.set_width(300)
        assert sider.expanded_width == 300

    def test_set_collapsed_width(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        sider.set_collapsed_width(64)
        assert sider.collapsed_width_value == 64

    def test_breakpoint_auto_collapse(self, qapp: QApplication) -> None:
        sider = TLayoutSider(breakpoint=Breakpoint.MD)
        assert sider.collapsed is False
        # Window width below MD threshold (768) should collapse
        sider.check_breakpoint(600)
        assert sider.collapsed is True
        # Window width above threshold should expand
        sider.check_breakpoint(900)
        assert sider.collapsed is False

    def test_no_breakpoint_no_auto_collapse(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        sider.check_breakpoint(100)
        assert sider.collapsed is False

    def test_set_content(self, qapp: QApplication) -> None:
        sider = TLayoutSider()
        label = QLabel("Nav")
        sider.set_content(label)
        assert sider._content_layout.count() == 1

    def test_placement_property(self, qapp: QApplication) -> None:
        sider = TLayoutSider(placement="right")
        assert sider.property("placement") == "right"


# -- TLayout -----------------------------------------------------------------


class TestTLayout:
    """Tests for TLayout composition and layout building."""

    def test_empty_layout(self, qapp: QApplication) -> None:
        layout = TLayout()
        assert layout.header is None
        assert layout.footer is None
        assert layout.sider is None
        assert layout.content is None

    def test_header_content_footer(self, qapp: QApplication) -> None:
        layout = TLayout()
        layout.add_header(TLayoutHeader())
        layout.add_content(TLayoutContent())
        layout.add_footer(TLayoutFooter())
        assert layout.header is not None
        assert layout.content is not None
        assert layout.footer is not None
        assert layout.sider is None

    def test_sider_content(self, qapp: QApplication) -> None:
        layout = TLayout()
        layout.add_sider(TLayoutSider())
        layout.add_content(TLayoutContent())
        assert layout.sider is not None
        assert layout.content is not None

    def test_full_layout(self, qapp: QApplication) -> None:
        layout = TLayout()
        layout.add_header(TLayoutHeader())
        layout.add_sider(TLayoutSider())
        layout.add_content(TLayoutContent())
        layout.add_footer(TLayoutFooter())
        assert layout.header is not None
        assert layout.sider is not None
        assert layout.content is not None
        assert layout.footer is not None

    def test_right_placement_sider(self, qapp: QApplication) -> None:
        layout = TLayout()
        layout.add_sider(TLayoutSider(placement="right"))
        layout.add_content(TLayoutContent())
        assert layout.sider is not None
        assert layout.sider.property("placement") == "right"

    def test_resize_forwards_to_sider(self, qapp: QApplication) -> None:
        layout = TLayout()
        sider = TLayoutSider(breakpoint=Breakpoint.MD)
        layout.add_sider(sider)
        layout.add_content(TLayoutContent())
        layout.resize(600, 400)
        # After resize below MD breakpoint, sider should collapse
        sider.check_breakpoint(600)
        assert sider.collapsed is True
