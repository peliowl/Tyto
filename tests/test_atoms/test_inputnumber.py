"""Unit tests for TInputNumber component."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from tyto_ui_lib.components.atoms.inputnumber import TInputNumber


class TestTInputNumberBasic:
    """Basic functionality tests for TInputNumber."""

    def test_default_value(self, qtbot):
        """Default value should be 0."""
        w = TInputNumber()
        qtbot.addWidget(w)
        assert w.get_value() == 0

    def test_initial_value(self, qtbot):
        """Constructor value should be respected."""
        w = TInputNumber(value=42)
        qtbot.addWidget(w)
        assert w.get_value() == 42

    def test_set_value(self, qtbot):
        """set_value should update the value."""
        w = TInputNumber(value=0, min=0, max=100)
        qtbot.addWidget(w)
        w.set_value(50)
        assert w.get_value() == 50

    def test_value_clamped_to_min(self, qtbot):
        """Values below min should be clamped."""
        w = TInputNumber(value=0, min=10, max=100)
        qtbot.addWidget(w)
        assert w.get_value() == 10

    def test_value_clamped_to_max(self, qtbot):
        """Values above max should be clamped."""
        w = TInputNumber(value=200, min=0, max=100)
        qtbot.addWidget(w)
        assert w.get_value() == 100

    def test_set_value_clamps(self, qtbot):
        """set_value should clamp to range."""
        w = TInputNumber(value=50, min=0, max=100)
        qtbot.addWidget(w)
        w.set_value(150)
        assert w.get_value() == 100
        w.set_value(-10)
        assert w.get_value() == 0


class TestTInputNumberStep:
    """Step and keyboard arrow tests."""

    def test_step_up_via_button(self, qtbot):
        """Plus button should increment by step."""
        w = TInputNumber(value=5, step=3, min=0, max=100)
        qtbot.addWidget(w)
        w.show()
        QTest.mouseClick(w._btn_plus, Qt.MouseButton.LeftButton)
        assert w.get_value() == 8

    def test_step_down_via_button(self, qtbot):
        """Minus button should decrement by step."""
        w = TInputNumber(value=10, step=3, min=0, max=100)
        qtbot.addWidget(w)
        w.show()
        QTest.mouseClick(w._btn_minus, Qt.MouseButton.LeftButton)
        assert w.get_value() == 7

    def test_step_respects_max(self, qtbot):
        """Stepping up should not exceed max."""
        w = TInputNumber(value=99, step=5, min=0, max=100)
        qtbot.addWidget(w)
        w.show()
        QTest.mouseClick(w._btn_plus, Qt.MouseButton.LeftButton)
        assert w.get_value() == 100

    def test_step_respects_min(self, qtbot):
        """Stepping down should not go below min."""
        w = TInputNumber(value=2, step=5, min=0, max=100)
        qtbot.addWidget(w)
        w.show()
        QTest.mouseClick(w._btn_minus, Qt.MouseButton.LeftButton)
        assert w.get_value() == 0

    def test_keyboard_up(self, qtbot):
        """Up arrow key should increment."""
        w = TInputNumber(value=10, step=1, min=0, max=100)
        qtbot.addWidget(w)
        w.show()
        w._line_edit.setFocus()
        QTest.keyClick(w._line_edit, Qt.Key.Key_Up)
        assert w.get_value() == 11

    def test_keyboard_down(self, qtbot):
        """Down arrow key should decrement."""
        w = TInputNumber(value=10, step=1, min=0, max=100)
        qtbot.addWidget(w)
        w.show()
        w._line_edit.setFocus()
        QTest.keyClick(w._line_edit, Qt.Key.Key_Down)
        assert w.get_value() == 9


class TestTInputNumberPrecision:
    """Precision and formatting tests."""

    def test_integer_mode(self, qtbot):
        """precision=0 should return int."""
        w = TInputNumber(value=5, precision=0)
        qtbot.addWidget(w)
        assert isinstance(w.get_value(), int)
        assert w.get_value() == 5

    def test_float_precision(self, qtbot):
        """precision=2 should return float with correct rounding."""
        w = TInputNumber(value=3.14159, precision=2)
        qtbot.addWidget(w)
        assert w.get_value() == 3.14

    def test_display_format(self, qtbot):
        """Display text should match precision format."""
        w = TInputNumber(value=1.5, precision=3)
        qtbot.addWidget(w)
        assert w._line_edit.text() == "1.500"


class TestTInputNumberSignal:
    """Signal emission tests."""

    def test_value_changed_on_set(self, qtbot):
        """value_changed should emit when value changes via set_value."""
        w = TInputNumber(value=0, min=0, max=100)
        qtbot.addWidget(w)
        with qtbot.waitSignal(w.value_changed, timeout=1000) as blocker:
            w.set_value(42)
        assert blocker.args == [42]

    def test_no_signal_on_same_value(self, qtbot):
        """value_changed should not emit when value doesn't change."""
        w = TInputNumber(value=50, min=0, max=100)
        qtbot.addWidget(w)
        signals = []
        w.value_changed.connect(signals.append)
        w.set_value(50)
        assert len(signals) == 0


class TestTInputNumberSize:
    """Size variant tests."""

    def test_default_size(self, qtbot):
        """Default size should be MEDIUM."""
        w = TInputNumber()
        qtbot.addWidget(w)
        assert w.size == TInputNumber.InputNumberSize.MEDIUM

    def test_set_size(self, qtbot):
        """set_size should update the size property."""
        w = TInputNumber()
        qtbot.addWidget(w)
        w.set_size(TInputNumber.InputNumberSize.SMALL)
        assert w.size == TInputNumber.InputNumberSize.SMALL
        assert w.property("inputNumberSize") == "small"


class TestTInputNumberDisabled:
    """Disabled state tests."""

    def test_disabled_blocks_step(self, qtbot):
        """Disabled component should not respond to step."""
        w = TInputNumber(value=5, min=0, max=100, disabled=True)
        qtbot.addWidget(w)
        w.show()
        w._step_value(1)
        assert w.get_value() == 5

    def test_set_disabled(self, qtbot):
        """set_disabled should update the disabled state."""
        w = TInputNumber(value=5)
        qtbot.addWidget(w)
        w.set_disabled(True)
        assert w.is_disabled is True
        assert w.property("disabled") == "true"
