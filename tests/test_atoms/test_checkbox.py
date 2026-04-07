"""Unit tests for TCheckbox atom component."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.checkbox import TCheckbox
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


class TestTCheckboxCreation:
    """Tests for TCheckbox initialization."""

    def test_default_state_unchecked(self, qapp: QApplication) -> None:
        cb = TCheckbox("Option")
        assert cb.get_state() == TCheckbox.CheckState.UNCHECKED

    def test_initial_checked(self, qapp: QApplication) -> None:
        cb = TCheckbox("Option", state=TCheckbox.CheckState.CHECKED)
        assert cb.get_state() == TCheckbox.CheckState.CHECKED

    def test_initial_indeterminate(self, qapp: QApplication) -> None:
        cb = TCheckbox("Option", state=TCheckbox.CheckState.INDETERMINATE)
        assert cb.get_state() == TCheckbox.CheckState.INDETERMINATE


class TestTCheckboxStateChanges:
    """Tests for state transitions and signal emission."""

    def test_set_state_emits_signal(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test")
        received: list[int] = []
        cb.state_changed.connect(received.append)
        cb.set_state(TCheckbox.CheckState.CHECKED)
        assert received == [TCheckbox.CheckState.CHECKED]
        assert cb.get_state() == TCheckbox.CheckState.CHECKED

    def test_set_state_same_no_signal(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test")
        received: list[int] = []
        cb.state_changed.connect(received.append)
        cb.set_state(TCheckbox.CheckState.UNCHECKED)
        assert received == []

    def test_toggle_unchecked_to_checked(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test")
        cb.toggle()
        assert cb.get_state() == TCheckbox.CheckState.CHECKED

    def test_toggle_checked_to_unchecked(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test", state=TCheckbox.CheckState.CHECKED)
        cb.toggle()
        assert cb.get_state() == TCheckbox.CheckState.UNCHECKED

    def test_click_toggles_state(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test")
        received: list[int] = []
        cb.state_changed.connect(received.append)
        cb.mousePressEvent(_make_left_click())
        assert cb.get_state() == TCheckbox.CheckState.CHECKED
        assert len(received) == 1

    def test_set_indeterminate(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test")
        cb.set_state(TCheckbox.CheckState.INDETERMINATE)
        assert cb.get_state() == TCheckbox.CheckState.INDETERMINATE
        assert cb.property("checkState") == "indeterminate"

    def test_round_trip_all_states(self, qapp: QApplication) -> None:
        cb = TCheckbox("Test")
        for state in TCheckbox.CheckState:
            cb.set_state(state)
            assert cb.get_state() == state
