"""Unit tests for TSpin atom component."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel

from tyto_ui_lib.components.atoms.spin import TSpin
from tyto_ui_lib.core.theme_engine import ThemeEngine

import pytest


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTSpinCreation:
    """Tests for TSpin initialization and default values."""

    def test_default_standalone_spinning(self, qapp: QApplication) -> None:
        spin = TSpin()
        assert spin.is_spinning() is True
        assert spin.mode == TSpin.SpinMode.STANDALONE
        assert spin.animation_type == TSpin.AnimationType.RING
        assert spin.size == TSpin.SpinSize.MEDIUM

    def test_initial_not_spinning(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=False)
        assert spin.is_spinning() is False

    def test_nested_mode(self, qapp: QApplication) -> None:
        spin = TSpin(mode=TSpin.SpinMode.NESTED)
        assert spin.mode == TSpin.SpinMode.NESTED
        assert spin._overlay is not None
        assert spin._content_widget is not None

    def test_standalone_no_overlay(self, qapp: QApplication) -> None:
        spin = TSpin(mode=TSpin.SpinMode.STANDALONE)
        assert spin._overlay is None

    def test_description_visible(self, qapp: QApplication) -> None:
        spin = TSpin(description="Loading...")
        assert spin.description == "Loading..."
        assert not spin._desc_label.isHidden()
        assert spin._desc_label.text() == "Loading..."

    def test_description_hidden_when_empty(self, qapp: QApplication) -> None:
        spin = TSpin(description="")
        assert spin._desc_label.isHidden()

    def test_delay_stored(self, qapp: QApplication) -> None:
        spin = TSpin(delay=500)
        assert spin.delay == 500

    def test_negative_delay_clamped(self, qapp: QApplication) -> None:
        spin = TSpin(delay=-100)
        assert spin.delay == 0

    def test_qss_properties(self, qapp: QApplication) -> None:
        spin = TSpin(
            mode=TSpin.SpinMode.NESTED,
            size=TSpin.SpinSize.LARGE,
            animation_type=TSpin.AnimationType.DOTS,
        )
        assert spin.property("spinMode") == "nested"
        assert spin.property("spinSize") == "large"
        assert spin.property("animationType") == "dots"


class TestTSpinSpinningState:
    """Tests for spinning state changes and signal emission."""

    def test_set_spinning_emits_signal(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=False)
        received: list[bool] = []
        spin.spinning_changed.connect(received.append)
        spin.set_spinning(True)
        assert received == [True]

    def test_set_spinning_false_emits_signal(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=True)
        received: list[bool] = []
        spin.spinning_changed.connect(received.append)
        spin.set_spinning(False)
        assert received == [False]

    def test_set_spinning_same_value_no_signal(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=True)
        received: list[bool] = []
        spin.spinning_changed.connect(received.append)
        spin.set_spinning(True)
        assert received == []

    def test_round_trip(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=False)
        spin.set_spinning(True)
        assert spin.is_spinning() is True
        spin.set_spinning(False)
        assert spin.is_spinning() is False


class TestTSpinNestedMode:
    """Tests for nested mode overlay behavior."""

    def test_overlay_hidden_when_not_spinning(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=False, mode=TSpin.SpinMode.NESTED)
        assert spin._overlay is not None
        assert spin._overlay.isHidden()

    def test_overlay_visible_when_spinning(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=True, mode=TSpin.SpinMode.NESTED)
        assert spin._overlay is not None
        assert not spin._overlay.isHidden()

    def test_set_content(self, qapp: QApplication) -> None:
        spin = TSpin(mode=TSpin.SpinMode.NESTED)
        label = QLabel("Test content")
        spin.set_content(label)
        assert spin._content_widget is not None
        layout = spin._content_widget.layout()
        assert layout is not None
        assert layout.count() == 1

    def test_set_content_standalone_noop(self, qapp: QApplication) -> None:
        spin = TSpin(mode=TSpin.SpinMode.STANDALONE)
        label = QLabel("Test content")
        spin.set_content(label)  # Should not raise


class TestTSpinCleanup:
    """Tests for cleanup behavior."""

    def test_cleanup_stops_timers(self, qapp: QApplication) -> None:
        spin = TSpin(spinning=True)
        spin.cleanup()
        assert not spin._delay_timer.isActive()
        assert not spin._indicator._timer.isActive()
