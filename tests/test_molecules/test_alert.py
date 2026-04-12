"""Unit tests for TAlert molecule component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QPushButton

from tyto_ui_lib.components.molecules.alert import TAlert
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTAlertCreation:
    """Tests for TAlert initialization and properties."""

    def test_default_type_is_info(self, qapp: QApplication) -> None:
        alert = TAlert()
        assert alert.alert_type == TAlert.AlertType.INFO

    def test_custom_type(self, qapp: QApplication) -> None:
        alert = TAlert(alert_type=TAlert.AlertType.ERROR)
        assert alert.alert_type == TAlert.AlertType.ERROR
        assert alert.property("alertType") == "error"

    def test_title_and_description(self, qapp: QApplication) -> None:
        alert = TAlert(title="Title", description="Desc")
        assert alert.title == "Title"
        assert alert.description == "Desc"

    def test_closable_default_false(self, qapp: QApplication) -> None:
        alert = TAlert()
        assert alert.closable is False
        assert alert._close_btn is None

    def test_closable_true_creates_button(self, qapp: QApplication) -> None:
        alert = TAlert(closable=True)
        assert alert.closable is True
        assert alert._close_btn is not None

    def test_bordered_default_true(self, qapp: QApplication) -> None:
        alert = TAlert()
        assert alert.bordered is True
        assert alert.property("bordered") == "true"

    def test_bordered_setter(self, qapp: QApplication) -> None:
        alert = TAlert()
        alert.bordered = False
        assert alert.bordered is False
        assert alert.property("bordered") == "false"

    def test_all_alert_types(self, qapp: QApplication) -> None:
        for at in TAlert.AlertType:
            alert = TAlert(alert_type=at)
            assert alert.alert_type == at
            assert alert.property("alertType") == at.value


class TestTAlertSignals:
    """Tests for closed signal."""

    def test_close_emits_closed_and_hides(self, qapp: QApplication) -> None:
        alert = TAlert(closable=True)
        received: list[bool] = []
        alert.closed.connect(lambda: received.append(True))
        # Directly call the fade-finished handler to avoid animation timing
        alert._on_fade_finished()
        assert len(received) == 1
        assert not alert.isVisible()


class TestTAlertAction:
    """Tests for set_action method."""

    def test_set_action_embeds_widget(self, qapp: QApplication) -> None:
        alert = TAlert(title="Test")
        btn = QPushButton("Action")
        alert.set_action(btn)
        assert alert._action_widget is btn

    def test_set_action_replaces_previous(self, qapp: QApplication) -> None:
        alert = TAlert(title="Test")
        btn1 = QPushButton("First")
        btn2 = QPushButton("Second")
        alert.set_action(btn1)
        alert.set_action(btn2)
        assert alert._action_widget is btn2
