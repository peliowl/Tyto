"""Unit tests for ContainerQueryMixin."""

from __future__ import annotations

import logging

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.container_query import ContainerQueryMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class CQWidget(ContainerQueryMixin, BaseWidget):
    """Test widget combining ContainerQueryMixin with BaseWidget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_container_query()


class TestContainerQueryMixin:
    def test_initial_breakpoint_is_none(self, qapp: QApplication) -> None:
        w = CQWidget()
        assert w.current_breakpoint() is None

    def test_add_breakpoint_and_match(self, qapp: QApplication) -> None:
        parent = QWidget()
        parent.resize(500, 300)
        w = CQWidget(parent)
        w._init_container_query()
        w.add_breakpoint("compact", 0, 400)
        w.add_breakpoint("normal", 401, 800)
        w._install_resize_filter()
        assert w.current_breakpoint() == "normal"

    def test_breakpoint_changed_signal_emitted(self, qapp: QApplication) -> None:
        parent = QWidget()
        parent.resize(300, 200)
        w = CQWidget(parent)
        w._init_container_query()
        w.add_breakpoint("compact", 0, 400)
        w.add_breakpoint("normal", 401, 800)

        received: list[str] = []
        w.breakpoint_changed.connect(received.append)

        w._install_resize_filter()
        assert w.current_breakpoint() == "compact"
        assert received == ["compact"]

    def test_container_resized_updates_breakpoint(self, qapp: QApplication) -> None:
        w = CQWidget()
        w._init_container_query()
        w.add_breakpoint("small", 0, 300)
        w.add_breakpoint("medium", 301, 600)
        w.add_breakpoint("large", 601, 1200)

        received: list[str] = []
        w.breakpoint_changed.connect(received.append)

        w.container_resized(200, 100)
        assert w.current_breakpoint() == "small"

        w.container_resized(500, 100)
        assert w.current_breakpoint() == "medium"

        w.container_resized(800, 100)
        assert w.current_breakpoint() == "large"

        assert received == ["small", "medium", "large"]

    def test_no_signal_when_breakpoint_unchanged(self, qapp: QApplication) -> None:
        w = CQWidget()
        w._init_container_query()
        w.add_breakpoint("compact", 0, 400)

        received: list[str] = []
        w.breakpoint_changed.connect(received.append)

        w.container_resized(100, 50)
        w.container_resized(200, 50)
        w.container_resized(300, 50)

        # Only one signal since breakpoint stays "compact"
        assert len(received) == 1
        assert received[0] == "compact"

    def test_no_match_returns_none(self, qapp: QApplication) -> None:
        w = CQWidget()
        w._init_container_query()
        w.add_breakpoint("compact", 0, 400)

        w.container_resized(500, 100)
        assert w.current_breakpoint() is None

    def test_parent_none_logs_warning(self, qapp: QApplication, caplog: pytest.LogCaptureFixture) -> None:
        w = CQWidget()  # No parent
        w._init_container_query()
        with caplog.at_level(logging.WARNING):
            w._install_resize_filter()
        assert "parent is None" in caplog.text

    def test_resize_filter_responds_to_parent_resize(self, qapp: QApplication) -> None:
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QResizeEvent

        parent = QWidget()
        parent.resize(200, 100)
        w = CQWidget(parent)
        w._init_container_query()
        w.add_breakpoint("small", 0, 300)
        w.add_breakpoint("large", 301, 1000)

        received: list[str] = []
        w.breakpoint_changed.connect(received.append)

        w._install_resize_filter()
        assert w.current_breakpoint() == "small"

        # Send a synthetic QResizeEvent to the parent
        parent.resize(500, 300)
        resize_event = QResizeEvent(QSize(500, 300), QSize(200, 100))
        qapp.sendEvent(parent, resize_event)
        assert w.current_breakpoint() == "large"

    def test_reinstall_filter_on_reparent(self, qapp: QApplication) -> None:
        parent1 = QWidget()
        parent1.resize(200, 100)
        w = CQWidget(parent1)
        w._init_container_query()
        w.add_breakpoint("small", 0, 300)
        w.add_breakpoint("large", 301, 1000)
        w._install_resize_filter()
        assert w.current_breakpoint() == "small"

        # Reparent to a larger container
        parent2 = QWidget()
        parent2.resize(600, 400)
        w.setParent(parent2)
        w._install_resize_filter()
        assert w.current_breakpoint() == "large"
