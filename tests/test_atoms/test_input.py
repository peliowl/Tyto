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

    def test_clearable_action_visibility(self, qapp: QApplication) -> None:
        inp = TInput(clearable=True)
        assert inp._clear_action is not None
        assert not inp._clear_action.isVisible()
        inp.set_text("x")
        assert inp._clear_action.isVisible()
        inp.set_text("")
        assert not inp._clear_action.isVisible()

    def test_clear_action_click(self, qapp: QApplication) -> None:
        inp = TInput(clearable=True)
        inp.set_text("data")
        cleared: list[bool] = []
        inp.cleared.connect(lambda: cleared.append(True))
        assert inp._clear_action is not None
        inp._clear_action.trigger()
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

# ---------------------------------------------------------------------------
# Property-Based Tests
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st
from PySide6.QtGui import QAction


class TestTInputPBT:
    """Property-based tests for TInput clear action positioning."""

    # Feature: tyto-ui-lib-v1, Property 35: Input 清空按钮在 QLineEdit 内部
    # **Validates: Requirements 21.1, 21.2**
    @settings(max_examples=100, deadline=None)
    @given(text=st.text(min_size=1, max_size=100))
    def test_clear_action_is_trailing_inside_line_edit(self, qapp: QApplication, text: str) -> None:
        """For any non-empty text, a clearable TInput's QLineEdit contains a
        trailing QAction that is visible when text is present."""
        inp = TInput(clearable=True)
        inp.set_text(text)

        # The clear action must exist and be a child of the QLineEdit
        assert inp._clear_action is not None
        assert isinstance(inp._clear_action, QAction)
        assert inp._clear_action.parent() is inp._line_edit

        # The action must be among the QLineEdit's actions
        line_edit_actions = inp._line_edit.actions()
        assert inp._clear_action in line_edit_actions

        # The action must be visible when text is non-empty
        assert inp._clear_action.isVisible()
