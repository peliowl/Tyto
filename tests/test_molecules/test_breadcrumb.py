"""Unit tests for TBreadcrumb molecule component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.molecules.breadcrumb import BreadcrumbItem, TBreadcrumb
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTBreadcrumbCreation:
    """Tests for TBreadcrumb initialization."""

    def test_default_empty(self, qapp: QApplication) -> None:
        bc = TBreadcrumb()
        assert bc.get_items() == []

    def test_init_with_items(self, qapp: QApplication) -> None:
        items = [BreadcrumbItem("Home"), BreadcrumbItem("Settings")]
        bc = TBreadcrumb(items=items)
        result = bc.get_items()
        assert len(result) == 2
        assert result[0].label == "Home"
        assert result[1].label == "Settings"


class TestTBreadcrumbSetItems:
    """Tests for set_items / get_items round-trip."""

    def test_set_items_replaces(self, qapp: QApplication) -> None:
        bc = TBreadcrumb(items=[BreadcrumbItem("A")])
        bc.set_items([BreadcrumbItem("X"), BreadcrumbItem("Y")])
        result = bc.get_items()
        assert len(result) == 2
        assert result[0].label == "X"

    def test_get_items_returns_copy(self, qapp: QApplication) -> None:
        items = [BreadcrumbItem("A")]
        bc = TBreadcrumb(items=items)
        got = bc.get_items()
        got.append(BreadcrumbItem("B"))
        assert len(bc.get_items()) == 1


class TestTBreadcrumbSignals:
    """Tests for item_clicked signal."""

    def test_click_non_last_emits_signal(self, qapp: QApplication) -> None:
        items = [
            BreadcrumbItem("Home", "/home"),
            BreadcrumbItem("Settings", "/settings"),
            BreadcrumbItem("Profile", "/profile"),
        ]
        bc = TBreadcrumb(items=items)
        received: list[tuple[int, object]] = []
        bc.item_clicked.connect(lambda i, d: received.append((i, d)))

        from tyto_ui_lib.components.molecules.breadcrumb import _ClickableLabel

        clickable_labels = bc.findChildren(_ClickableLabel)
        assert len(clickable_labels) == 2
        clickable_labels[0].clicked.emit()
        assert received == [(0, "/home")]

    def test_last_item_not_clickable(self, qapp: QApplication) -> None:
        items = [BreadcrumbItem("Home"), BreadcrumbItem("Current")]
        bc = TBreadcrumb(items=items)

        from tyto_ui_lib.components.molecules.breadcrumb import _ClickableLabel

        clickable_labels = bc.findChildren(_ClickableLabel)
        assert len(clickable_labels) == 1
