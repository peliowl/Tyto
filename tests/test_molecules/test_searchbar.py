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
