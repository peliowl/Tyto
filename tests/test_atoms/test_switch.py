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


# ---------------------------------------------------------------------------
# V1.0.2 Property-Based Tests
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st


class TestTSwitchSizeVariant:
    """Property 58: Switch size variant correctness.

    For any SwitchSize enum value, creating a TSwitch with that size
    should result in the track's fixed size matching the switch_sizes
    Token dimensions for that size.

    **Validates: Requirements 35.1**
    """

    # Feature: tyto-ui-lib-v1, Property 58: Switch 尺寸变体正确性
    @settings(max_examples=100, deadline=None)
    @given(size=st.sampled_from(list(TSwitch.SwitchSize)))
    def test_switch_size_track_dimensions(self, qapp: QApplication, size: TSwitch.SwitchSize) -> None:
        """For any SwitchSize, the track dimensions match the token values."""
        from tyto_ui_lib.components.atoms.switch import _get_switch_dims

        sw = TSwitch(size=size)
        dims = _get_switch_dims(size.value)
        track = sw._track
        assert track.width() == dims["width"]
        assert track.height() == dims["height"]
        assert track._thumb_d == dims["thumb"]
        assert sw.property("switchSize") == size.value


class TestTSwitchLoadingBlocks:
    """Property 59: Switch loading blocks interaction.

    For any loading=True TSwitch, clicking should not change the switch
    state and the toggled signal should not be emitted.

    **Validates: Requirements 35.2**
    """

    # Feature: tyto-ui-lib-v1, Property 59: Switch Loading 屏蔽交互
    @settings(max_examples=100, deadline=None)
    @given(initial_checked=st.booleans())
    def test_switch_loading_blocks_click(self, qapp: QApplication, initial_checked: bool) -> None:
        """For any initial state with loading=True, click does not toggle."""
        sw = TSwitch(checked=initial_checked, loading=True)
        sw.resize(48, 28)
        received: list[bool] = []
        sw.toggled.connect(received.append)
        sw.mousePressEvent(_make_mouse_press())
        assert received == []
        assert sw.is_checked() is initial_checked


class TestTSwitchCustomValueRoundTrip:
    """Property 60: Switch custom value round-trip.

    For any checked_value and unchecked_value, TSwitch in checked state
    should return checked_value from get_typed_value(), and in unchecked
    state should return unchecked_value.

    **Validates: Requirements 35.4**
    """

    # Feature: tyto-ui-lib-v1, Property 60: Switch 自定义值 Round-Trip
    @settings(max_examples=100, deadline=None)
    @given(
        checked_val=st.one_of(st.integers(), st.text(min_size=1, max_size=20), st.booleans()),
        unchecked_val=st.one_of(st.integers(), st.text(min_size=1, max_size=20), st.booleans()),
    )
    def test_switch_typed_value_round_trip(
        self, qapp: QApplication, checked_val: object, unchecked_val: object
    ) -> None:
        """For any custom values, get_typed_value returns the correct one based on state."""
        sw = TSwitch(checked=False, checked_value=checked_val, unchecked_value=unchecked_val)
        assert sw.get_typed_value() == unchecked_val

        sw.set_checked(True)
        assert sw.get_typed_value() == checked_val

        sw.set_checked(False)
        assert sw.get_typed_value() == unchecked_val
