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



# ---------------------------------------------------------------------------
# Property-based tests for TCheckbox V1.0.2 enhanced features
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st


class TestTCheckboxSizeVariant:
    """Property-based tests for TCheckbox size variants."""

    # Feature: tyto-ui-lib-v1, Property 51: Checkbox 尺寸变体正确性
    # **Validates: Requirements 33.1**
    @settings(max_examples=100, deadline=None)
    @given(size=st.sampled_from(list(TCheckbox.CheckboxSize)))
    def test_size_property_matches(self, qapp: QApplication, size: TCheckbox.CheckboxSize) -> None:
        cb = TCheckbox("Test", size=size)
        assert cb.size == size
        assert cb.property("checkboxSize") == size.value


class TestTCheckboxDisabledState:
    """Property-based tests for TCheckbox disabled state."""

    # Feature: tyto-ui-lib-v1, Property 52: Checkbox Disabled 状态
    # **Validates: Requirements 33.2**
    @settings(max_examples=100, deadline=None)
    @given(state=st.sampled_from(list(TCheckbox.CheckState)))
    def test_disabled_blocks_click(self, qapp: QApplication, state: TCheckbox.CheckState) -> None:
        cb = TCheckbox("Test", state=state, disabled=True)
        received: list[int] = []
        cb.state_changed.connect(received.append)
        cb.mousePressEvent(_make_left_click())
        assert cb.get_state() == state
        assert received == []
