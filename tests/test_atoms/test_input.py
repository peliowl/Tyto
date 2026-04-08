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


# ---------------------------------------------------------------------------
# V1.0.2 Property-Based Tests - TInput Enhancement
# ---------------------------------------------------------------------------

from PySide6.QtWidgets import QPlainTextEdit


class TestTInputV102PBT:
    """Property-based tests for TInput V1.0.2 enhanced features."""

    # Feature: tyto-ui-lib-v1, Property 47: Input 尺寸变体正确性
    # **Validates: Requirements 32.1**
    @settings(max_examples=100, deadline=None)
    @given(size=st.sampled_from(list(TInput.InputSize)))
    def test_input_size_variant_correctness(self, qapp: QApplication, size: TInput.InputSize) -> None:
        """For any InputSize, creating a TInput with that size should set the
        size property and QSS dynamic property correctly."""
        inp = TInput(size=size)
        assert inp.size == size
        assert inp.property("inputSize") == size.value

    # Feature: tyto-ui-lib-v1, Property 48: Input Textarea 模式切换
    # **Validates: Requirements 32.2, 32.3**
    @settings(max_examples=100, deadline=None)
    @given(placeholder=st.text(min_size=0, max_size=50))
    def test_input_textarea_mode(self, qapp: QApplication, placeholder: str) -> None:
        """For any input_type=TEXTAREA TInput, the internal editor should be
        a QPlainTextEdit, not a QLineEdit."""
        inp = TInput(input_type=TInput.InputType.TEXTAREA, placeholder=placeholder)
        assert inp.input_type == TInput.InputType.TEXTAREA
        assert inp._text_edit is not None
        assert isinstance(inp._text_edit, QPlainTextEdit)
        assert inp._line_edit is None

    # Feature: tyto-ui-lib-v1, Property 49: Input Maxlength 约束
    # **Validates: Requirements 32.6**
    @settings(max_examples=100, deadline=None)
    @given(
        maxlength=st.integers(min_value=1, max_value=50),
        text=st.text(min_size=1, max_size=100),
    )
    def test_input_maxlength_constraint(
        self, qapp: QApplication, maxlength: int, text: str
    ) -> None:
        """For any positive maxlength and any text, the resulting text length
        should never exceed maxlength."""
        inp = TInput(maxlength=maxlength)
        inp.set_text(text)
        assert len(inp.get_text()) <= maxlength

    # Feature: tyto-ui-lib-v1, Property 50: Input Status 边框颜色
    # **Validates: Requirements 32.13**
    @settings(max_examples=100, deadline=None)
    @given(status=st.sampled_from(list(TInput.InputStatus)))
    def test_input_status_property(self, qapp: QApplication, status: TInput.InputStatus) -> None:
        """For any InputStatus, setting status should update the QSS dynamic
        property correctly."""
        inp = TInput(status=status)
        assert inp.status == status
        assert inp.property("status") == status.value
