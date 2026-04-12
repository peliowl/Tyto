"""Unit tests for TBackTop atom component."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QScrollArea, QWidget, QVBoxLayout

from tyto_ui_lib.components.atoms.backtop import TBackTop
from tyto_ui_lib.core.theme_engine import ThemeEngine

import pytest


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


def _make_scroll_area(qapp: QApplication) -> QScrollArea:
    """Create a QScrollArea with tall content to enable scrolling."""
    scroll = QScrollArea()
    scroll.setFixedSize(300, 200)
    content = QWidget()
    content.setFixedSize(280, 2000)
    scroll.setWidget(content)
    scroll.show()
    return scroll


class TestTBackTopCreation:
    """Tests for TBackTop initialization and default values."""

    def test_default_visibility_height(self, qapp: QApplication) -> None:
        bt = TBackTop()
        assert bt.visibility_height == 200

    def test_custom_visibility_height(self, qapp: QApplication) -> None:
        bt = TBackTop(visibility_height=500)
        assert bt.visibility_height == 500

    def test_default_offsets(self, qapp: QApplication) -> None:
        bt = TBackTop()
        assert bt.right_offset == 40
        assert bt.bottom_offset == 40

    def test_custom_offsets(self, qapp: QApplication) -> None:
        bt = TBackTop(right=20, bottom=30)
        assert bt.right_offset == 20
        assert bt.bottom_offset == 30

    def test_initially_hidden(self, qapp: QApplication) -> None:
        bt = TBackTop()
        assert not bt.isVisible()

    def test_default_arrow_label(self, qapp: QApplication) -> None:
        bt = TBackTop()
        # The icon is now painted directly in paintEvent, no QLabel
        assert bt._custom_content is None


class TestTBackTopTarget:
    """Tests for target scroll area monitoring."""

    def test_set_target(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop()
        bt.set_target(scroll)
        assert bt._target is scroll

    def test_target_via_constructor(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop(target=scroll)
        assert bt._target is scroll

    def test_hidden_when_scroll_below_threshold(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop(target=scroll, visibility_height=200)
        vbar = scroll.verticalScrollBar()
        assert vbar is not None
        vbar.setValue(100)
        qapp.processEvents()
        assert bt._fade_target == 0.0

    def test_visible_when_scroll_above_threshold(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop(target=scroll, visibility_height=200)
        vbar = scroll.verticalScrollBar()
        assert vbar is not None
        vbar.setValue(300)
        qapp.processEvents()
        assert bt._fade_target == 1.0


class TestTBackTopClick:
    """Tests for click behavior and signal emission."""

    def test_clicked_signal(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop(target=scroll)
        received: list[bool] = []
        bt.clicked.connect(lambda: received.append(True))
        bt.mousePressEvent(None)
        assert received == [True]

    def test_scroll_to_top_starts_timer(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop(target=scroll)
        vbar = scroll.verticalScrollBar()
        assert vbar is not None
        vbar.setValue(500)
        qapp.processEvents()
        bt._scroll_to_top()
        assert bt._scroll_timer.isActive()
        bt._scroll_timer.stop()


class TestTBackTopContent:
    """Tests for custom content."""

    def test_set_content(self, qapp: QApplication) -> None:
        bt = TBackTop()
        custom = QLabel("Top")
        bt.set_content(custom)
        assert bt._custom_content is custom

    def test_replace_content(self, qapp: QApplication) -> None:
        bt = TBackTop()
        c1 = QLabel("A")
        c2 = QLabel("B")
        bt.set_content(c1)
        bt.set_content(c2)
        assert bt._custom_content is c2


class TestTBackTopCleanup:
    """Tests for cleanup behavior."""

    def test_cleanup_stops_timers(self, qapp: QApplication) -> None:
        scroll = _make_scroll_area(qapp)
        bt = TBackTop(target=scroll)
        vbar = scroll.verticalScrollBar()
        assert vbar is not None
        vbar.setValue(500)
        qapp.processEvents()
        bt._scroll_to_top()
        bt.cleanup()
        assert not bt._scroll_timer.isActive()
        assert not bt._fade_timer.isActive()
