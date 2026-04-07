"""Unit tests for TRadio and TRadioGroup atom components."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.radio import TRadio, TRadioGroup
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


def _make_left_click() -> QMouseEvent:
    p = QPointF(5, 5)
    return QMouseEvent(
        QEvent.Type.MouseButtonPress, p, p,
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


class TestTRadioCreation:
    """Tests for TRadio initialization."""

    def test_default_unchecked(self, qapp: QApplication) -> None:
        radio = TRadio("Option A", value="a")
        assert radio.is_checked() is False
        assert radio.value == "a"

    def test_initial_checked(self, qapp: QApplication) -> None:
        radio = TRadio("Option B", value="b", checked=True)
        assert radio.is_checked() is True

    def test_set_checked_emits_toggled(self, qapp: QApplication) -> None:
        radio = TRadio("Test", value=1)
        received: list[bool] = []
        radio.toggled.connect(received.append)
        radio.set_checked(True)
        assert received == [True]

    def test_set_checked_same_no_signal(self, qapp: QApplication) -> None:
        radio = TRadio("Test", value=1, checked=True)
        received: list[bool] = []
        radio.toggled.connect(received.append)
        radio.set_checked(True)
        assert received == []

    def test_click_checks_radio(self, qapp: QApplication) -> None:
        radio = TRadio("Test", value="x")
        received: list[bool] = []
        radio.toggled.connect(received.append)
        radio.mousePressEvent(_make_left_click())
        assert radio.is_checked() is True
        assert received == [True]


class TestTRadioGroup:
    """Tests for TRadioGroup mutual exclusion."""

    def test_mutual_exclusion(self, qapp: QApplication) -> None:
        group = TRadioGroup()
        r1 = TRadio("A", value="a")
        r2 = TRadio("B", value="b")
        r3 = TRadio("C", value="c")
        group.add_radio(r1)
        group.add_radio(r2)
        group.add_radio(r3)

        r1.set_checked(True)
        assert r1.is_checked() is True
        assert group.get_selected_value() == "a"

        r2.set_checked(True)
        assert r2.is_checked() is True
        assert r1.is_checked() is False
        assert group.get_selected_value() == "b"

    def test_selection_changed_signal(self, qapp: QApplication) -> None:
        group = TRadioGroup()
        r1 = TRadio("A", value="a")
        r2 = TRadio("B", value="b")
        group.add_radio(r1)
        group.add_radio(r2)

        received: list[object] = []
        group.selection_changed.connect(received.append)

        r1.set_checked(True)
        assert received == ["a"]

        r2.set_checked(True)
        assert received == ["a", "b"]

    def test_no_selection_returns_none(self, qapp: QApplication) -> None:
        group = TRadioGroup()
        r1 = TRadio("A", value="a")
        group.add_radio(r1)
        assert group.get_selected_value() is None

    def test_click_triggers_exclusion(self, qapp: QApplication) -> None:
        group = TRadioGroup()
        r1 = TRadio("A", value="a")
        r2 = TRadio("B", value="b")
        group.add_radio(r1)
        group.add_radio(r2)

        r1.mousePressEvent(_make_left_click())
        assert r1.is_checked() is True

        r2.mousePressEvent(_make_left_click())
        assert r2.is_checked() is True
        assert r1.is_checked() is False
