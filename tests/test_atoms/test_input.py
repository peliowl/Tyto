"""Unit tests for TInput atom component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLineEdit

from tyto_ui_lib.components.atoms.input import TInput
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTInputCreation:
    """Tests for TInput initialization."""

    def test_default_empty(self, qapp: QApplication) -> None:
        inp = TInput()
        assert inp.get_text() == ""

    def test_placeholder(self, qapp: QApplication) -> None:
        inp = TInput(placeholder="Search...")
        assert inp._line_edit.placeholderText() == "Search..."

    def test_password_mode(self, qapp: QApplication) -> None:
        inp = TInput(password=True)
        assert inp._line_edit.echoMode() == QLineEdit.EchoMode.Password


class TestTInputTextChanges:
    """Tests for text changes and signals."""

    def test_set_text_emits_signal(self, qapp: QApplication) -> None:
        inp = TInput()
        received: list[str] = []
        inp.text_changed.connect(received.append)
        inp.set_text("hello")
        assert received == ["hello"]
        assert inp.get_text() == "hello"

    def test_clear_emits_cleared(self, qapp: QApplication) -> None:
        inp = TInput(clearable=True)
        inp.set_text("some text")
        cleared: list[bool] = []
        inp.cleared.connect(lambda: cleared.append(True))
        inp.clear()
        assert inp.get_text() == ""
        assert len(cleared) == 1

    def test_clearable_button_visibility(self, qapp: QApplication) -> None:
        inp = TInput(clearable=True)
        assert inp._clear_btn is not None
        assert inp._clear_btn.isHidden()
        inp.set_text("x")
        assert not inp._clear_btn.isHidden()
        inp.set_text("")
        assert inp._clear_btn.isHidden()

    def test_clear_button_click(self, qapp: QApplication) -> None:
        inp = TInput(clearable=True)
        inp.set_text("data")
        cleared: list[bool] = []
        inp.cleared.connect(lambda: cleared.append(True))
        inp._clear_btn.click()  # type: ignore[union-attr]
        assert inp.get_text() == ""
        assert len(cleared) == 1


class TestTInputPassword:
    """Tests for password mode behavior."""

    def test_toggle_visibility(self, qapp: QApplication) -> None:
        inp = TInput(password=True)
        assert inp._line_edit.echoMode() == QLineEdit.EchoMode.Password

        inp.toggle_password_visibility()
        assert inp._line_edit.echoMode() == QLineEdit.EchoMode.Normal

        inp.toggle_password_visibility()
        assert inp._line_edit.echoMode() == QLineEdit.EchoMode.Password

    def test_toggle_noop_without_password(self, qapp: QApplication) -> None:
        inp = TInput(password=False)
        inp.toggle_password_visibility()
        assert inp._line_edit.echoMode() == QLineEdit.EchoMode.Normal
