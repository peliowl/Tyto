"""Property-based tests for TRadio, TRadioButton, and TRadioGroup enhanced features."""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.radio import TRadio, TRadioButton, TRadioGroup
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


# -- Strategies --
radio_sizes = st.sampled_from(list(TRadio.RadioSize))


# Feature: tyto-ui-lib-v1, Property 55: Radio 尺寸变体正确性
# **Validates: Requirements 34.1**
class TestProperty55RadioSizeVariant:
    """For any RadioSize, creating a TRadio with that size should set the size property correctly."""

    @settings(max_examples=100)
    @given(size=radio_sizes)
    def test_radio_size_property(self, qapp: QApplication, size: TRadio.RadioSize) -> None:
        radio = TRadio("Test", value="t", size=size)
        assert radio.size == size
        assert radio.property("radioSize") == size.value

    @settings(max_examples=100)
    @given(size=radio_sizes)
    def test_radio_set_size(self, qapp: QApplication, size: TRadio.RadioSize) -> None:
        radio = TRadio("Test", value="t")
        radio.set_size(size)
        assert radio.size == size
        assert radio.property("radioSize") == size.value


# Feature: tyto-ui-lib-v1, Property 56: Radio Disabled 状态
# **Validates: Requirements 34.2**
class TestProperty56RadioDisabled:
    """For any disabled=True TRadio, clicking should not change state or emit toggled."""

    @settings(max_examples=100)
    @given(size=radio_sizes)
    def test_disabled_blocks_click(self, qapp: QApplication, size: TRadio.RadioSize) -> None:
        radio = TRadio("Test", value="t", size=size, disabled=True)
        received: list[bool] = []
        radio.toggled.connect(received.append)
        radio.mousePressEvent(_make_left_click())
        assert radio.is_checked() is False
        assert received == []

    @settings(max_examples=100)
    @given(size=radio_sizes)
    def test_disabled_state_properties(self, qapp: QApplication, size: TRadio.RadioSize) -> None:
        radio = TRadio("Test", value="t", size=size, disabled=True)
        assert radio.is_disabled() is True
        assert radio.isEnabled() is False


# Feature: tyto-ui-lib-v1, Property 57: RadioButton 互斥不变量
# **Validates: Requirements 34.4, 34.9**
class TestProperty57RadioButtonMutualExclusion:
    """For any TRadioGroup with TRadioButton items, selecting one should deselect all others."""

    @settings(max_examples=100)
    @given(selected_idx=st.integers(min_value=0, max_value=2))
    def test_button_mode_mutual_exclusion(self, qapp: QApplication, selected_idx: int) -> None:
        group = TRadioGroup()
        buttons = [
            TRadioButton("A", value="a"),
            TRadioButton("B", value="b"),
            TRadioButton("C", value="c"),
        ]
        for btn in buttons:
            group.add_radio(btn)

        assert group.is_button_mode() is True

        buttons[selected_idx].set_checked(True)

        checked_count = sum(1 for b in buttons if b.is_checked())
        assert checked_count == 1
        assert buttons[selected_idx].is_checked() is True
        assert group.get_selected_value() == buttons[selected_idx].value
