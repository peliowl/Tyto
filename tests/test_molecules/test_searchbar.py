"""Unit tests for TSearchBar molecule component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.molecules.searchbar import TSearchBar
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTSearchBarCreation:
    """Tests for TSearchBar initialization."""

    def test_default_empty(self, qapp: QApplication) -> None:
        bar = TSearchBar()
        assert bar.get_text() == ""

    def test_clearable_default_true(self, qapp: QApplication) -> None:
        bar = TSearchBar()
        assert bar._input._clearable is True


class TestTSearchBarSignals:
    """Tests for search_changed and search_submitted signals."""

    def test_search_changed_on_text_input(self, qapp: QApplication) -> None:
        bar = TSearchBar()
        received: list[str] = []
        bar.search_changed.connect(received.append)
        bar._input.set_text("hello")
        assert received == ["hello"]

    def test_search_submitted_on_button_click(self, qapp: QApplication) -> None:
        bar = TSearchBar()
        received: list[str] = []
        bar.search_submitted.connect(received.append)
        bar._input.set_text("query")
        bar._button.clicked.emit()
        assert received == ["query"]

    def test_clear(self, qapp: QApplication) -> None:
        bar = TSearchBar()
        bar._input.set_text("text")
        bar.clear()
        assert bar.get_text() == ""

class TestSearchBarClearButtonPosition:
    """Verify that TInput clear button fix (Task 20) propagates to SearchBar.

    The SearchBar's internal TInput should use a QAction inside QLineEdit
    for the clear button, not an external QToolButton.

    **Validates: Requirements 23.1, 23.2**
    """

    def test_searchbar_input_clear_action_inside_line_edit(self, qapp: QApplication) -> None:
        """SearchBar's TInput clear button is a QAction inside QLineEdit."""
        bar = TSearchBar(clearable=True)
        inp = bar._input

        # The clear action must exist and be parented to the QLineEdit
        assert inp._clear_action is not None
        assert inp._clear_action.parent() is inp._line_edit

        # It must be among the QLineEdit's own actions
        assert inp._clear_action in inp._line_edit.actions()

    def test_searchbar_input_clear_action_visible_with_text(self, qapp: QApplication) -> None:
        """SearchBar's clear action becomes visible when text is entered."""
        bar = TSearchBar(clearable=True)
        inp = bar._input

        assert inp._clear_action is not None
        assert not inp._clear_action.isVisible()

        bar._input.set_text("query")
        assert inp._clear_action.isVisible()

    def test_searchbar_clear_action_clears_and_emits(self, qapp: QApplication) -> None:
        """Triggering the clear action inside SearchBar clears text and emits cleared."""
        bar = TSearchBar(clearable=True)
        bar._input.set_text("hello")

        cleared: list[bool] = []
        bar._input.cleared.connect(lambda: cleared.append(True))

        assert bar._input._clear_action is not None
        bar._input._clear_action.trigger()

        assert bar.get_text() == ""
        assert len(cleared) == 1



class TestSearchBarClearButtonPosition:
    """Verify that TInput clear button fix (Task 20) propagates to SearchBar.

    The SearchBar's internal TInput should use a QAction inside QLineEdit
    for the clear button, not an external QToolButton.

    **Validates: Requirements 23.1, 23.2**
    """

    def test_searchbar_input_clear_action_inside_line_edit(self, qapp: QApplication) -> None:
        """SearchBar's TInput clear button is a QAction inside QLineEdit."""
        bar = TSearchBar(clearable=True)
        inp = bar._input

        # The clear action must exist and be parented to the QLineEdit
        assert inp._clear_action is not None
        assert inp._clear_action.parent() is inp._line_edit

        # It must be among the QLineEdit's own actions
        assert inp._clear_action in inp._line_edit.actions()

    def test_searchbar_input_clear_action_visible_with_text(self, qapp: QApplication) -> None:
        """SearchBar's clear action becomes visible when text is entered."""
        bar = TSearchBar(clearable=True)
        inp = bar._input

        assert inp._clear_action is not None
        assert not inp._clear_action.isVisible()

        bar._input.set_text("query")
        assert inp._clear_action.isVisible()

    def test_searchbar_clear_action_clears_and_emits(self, qapp: QApplication) -> None:
        """Triggering the clear action inside SearchBar clears text and emits cleared."""
        bar = TSearchBar(clearable=True)
        bar._input.set_text("hello")

        cleared: list[bool] = []
        bar._input.cleared.connect(lambda: cleared.append(True))

        assert bar._input._clear_action is not None
        bar._input._clear_action.trigger()

        assert bar.get_text() == ""
        assert len(cleared) == 1
