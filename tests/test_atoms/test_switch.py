"""Unit tests for TSwitch atom component."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.switch import TSwitch
from tyto_ui_lib.core.theme_engine import ThemeEngine

import pytest


def _make_mouse_press(pos: QPointF | None = None) -> QMouseEvent:
    p = pos or QPointF(5, 5)
    return QMouseEvent(
        QEvent.Type.MouseButtonPress, p, p,
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTSwitchCreation:
    """Tests for TSwitch initialization."""

    def test_default_unchecked(self, qapp: QApplication) -> None:
        sw = TSwitch()
        assert sw.is_checked() is False

    def test_initial_checked(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=True)
        assert sw.is_checked() is True

    def test_initial_disabled(self, qapp: QApplication) -> None:
        sw = TSwitch(disabled=True)
        assert not sw.isEnabled()


class TestTSwitchToggle:
    """Tests for toggle behavior and signal emission."""

    def test_toggle_changes_state(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=False)
        sw.toggle()
        assert sw.is_checked() is True
        sw.toggle()
        assert sw.is_checked() is False

    def test_toggle_emits_signal(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=False)
        received: list[bool] = []
        sw.toggled.connect(received.append)
        sw.toggle()
        assert received == [True]

    def test_set_checked_emits_signal(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=False)
        received: list[bool] = []
        sw.toggled.connect(received.append)
        sw.set_checked(True)
        assert received == [True]

    def test_set_checked_same_value_no_signal(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=False)
        received: list[bool] = []
        sw.toggled.connect(received.append)
        sw.set_checked(False)
        assert received == []

    def test_click_toggles(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=False)
        sw.resize(48, 28)
        received: list[bool] = []
        sw.toggled.connect(received.append)
        sw.mousePressEvent(_make_mouse_press())
        assert received == [True]
        assert sw.is_checked() is True

    def test_disabled_blocks_click(self, qapp: QApplication) -> None:
        sw = TSwitch(checked=False, disabled=True)
        sw.resize(48, 28)
        received: list[bool] = []
        sw.toggled.connect(received.append)
        sw.mousePressEvent(_make_mouse_press())
        assert received == []
        assert sw.is_checked() is False
