"""Unit tests for TSlider atom component."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.slider import TSlider, _snap_to_step
from tyto_ui_lib.core.theme_engine import ThemeEngine

import pytest


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestSnapToStep:
    """Tests for the _snap_to_step helper."""

    def test_snap_basic(self) -> None:
        assert _snap_to_step(7.0, 0.0, 100.0, 5.0) == 5.0

    def test_snap_exact(self) -> None:
        assert _snap_to_step(10.0, 0.0, 100.0, 5.0) == 10.0

    def test_snap_clamp_min(self) -> None:
        assert _snap_to_step(-5.0, 0.0, 100.0, 5.0) == 0.0

    def test_snap_clamp_max(self) -> None:
        assert _snap_to_step(105.0, 0.0, 100.0, 5.0) == 100.0

    def test_snap_zero_step(self) -> None:
        assert _snap_to_step(7.3, 0.0, 100.0, 0.0) == 7.3


class TestTSliderCreation:
    """Tests for TSlider initialization."""

    def test_default_value(self, qapp: QApplication) -> None:
        s = TSlider()
        assert s.value == 0.0

    def test_initial_value(self, qapp: QApplication) -> None:
        s = TSlider(value=50)
        assert s.value == 50.0

    def test_range_mode(self, qapp: QApplication) -> None:
        s = TSlider(value=(20, 80), range=True)
        val = s.value
        assert isinstance(val, tuple)
        assert val == (20.0, 80.0)

    def test_min_max(self, qapp: QApplication) -> None:
        s = TSlider(min_val=10, max_val=50, value=30)
        assert s.min_val == 10.0
        assert s.max_val == 50.0
        assert s.value == 30.0

    def test_step_snapping(self, qapp: QApplication) -> None:
        s = TSlider(value=7, step=5)
        assert s.value == 5.0

    def test_vertical_mode(self, qapp: QApplication) -> None:
        s = TSlider(vertical=True)
        assert s.is_vertical is True

    def test_disabled(self, qapp: QApplication) -> None:
        s = TSlider(disabled=True)
        assert s.is_disabled is True
        assert not s.isEnabled()

    def test_marks(self, qapp: QApplication) -> None:
        marks = {0: "0", 50: "50", 100: "100"}
        s = TSlider(marks=marks)
        assert s.marks == {0.0: "0", 50.0: "50", 100.0: "100"}


class TestTSliderSetValue:
    """Tests for set_value and value_changed signal."""

    def test_set_value_single(self, qapp: QApplication) -> None:
        s = TSlider(value=0)
        received: list[object] = []
        s.value_changed.connect(received.append)
        s.set_value(50)
        assert s.value == 50.0
        assert len(received) == 1
        assert received[0] == 50.0

    def test_set_value_range(self, qapp: QApplication) -> None:
        s = TSlider(value=(10, 90), range=True)
        received: list[object] = []
        s.value_changed.connect(received.append)
        s.set_value((30, 70))
        val = s.value
        assert isinstance(val, tuple)
        assert val == (30.0, 70.0)
        assert len(received) == 1

    def test_set_value_snaps_to_step(self, qapp: QApplication) -> None:
        s = TSlider(value=0, step=10)
        s.set_value(23)
        assert s.value == 20.0

    def test_range_value_order_enforced(self, qapp: QApplication) -> None:
        s = TSlider(value=(10, 90), range=True)
        s.set_value((80, 20))
        val = s.value
        assert isinstance(val, tuple)
        assert val[0] <= val[1]


class TestTSliderDisabled:
    """Tests for disabled state."""

    def test_set_disabled(self, qapp: QApplication) -> None:
        s = TSlider()
        s.set_disabled(True)
        assert s.is_disabled is True
        assert not s.isEnabled()
        s.set_disabled(False)
        assert s.is_disabled is False
        assert s.isEnabled()


class TestTSliderProperties:
    """Tests for property accessors."""

    def test_is_range(self, qapp: QApplication) -> None:
        assert TSlider(range=True).is_range is True
        assert TSlider(range=False).is_range is False

    def test_step_property(self, qapp: QApplication) -> None:
        s = TSlider(step=5)
        assert s.step == 5.0

    def test_set_marks(self, qapp: QApplication) -> None:
        s = TSlider()
        s.set_marks({25: "25%", 75: "75%"})
        assert s.marks == {25.0: "25%", 75.0: "75%"}
