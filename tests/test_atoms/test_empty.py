"""Unit tests for TEmpty atom component."""

from __future__ import annotations

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel

from tyto_ui_lib.components.atoms.empty import TEmpty
from tyto_ui_lib.core.theme_engine import ThemeEngine

import pytest


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTEmptyCreation:
    """Tests for TEmpty initialization and default values."""

    def test_default_description(self, qapp: QApplication) -> None:
        empty = TEmpty()
        assert empty.description == "暂无数据"

    def test_custom_description(self, qapp: QApplication) -> None:
        empty = TEmpty(description="No results")
        assert empty.description == "No results"
        assert empty._desc_label.text() == "No results"

    def test_default_image_size(self, qapp: QApplication) -> None:
        empty = TEmpty()
        assert empty.image_size == 96

    def test_custom_image_size(self, qapp: QApplication) -> None:
        empty = TEmpty(image_size=64)
        assert empty.image_size == 64

    def test_default_uses_svg(self, qapp: QApplication) -> None:
        empty = TEmpty()
        assert empty._svg_widget is not None
        assert empty._pixmap_label is None


class TestTEmptyDescription:
    """Tests for description text updates."""

    def test_set_description(self, qapp: QApplication) -> None:
        empty = TEmpty()
        empty.set_description("Nothing here")
        assert empty.description == "Nothing here"
        assert empty._desc_label.text() == "Nothing here"


class TestTEmptyImage:
    """Tests for custom image support."""

    def test_set_pixmap_image(self, qapp: QApplication) -> None:
        empty = TEmpty()
        pm = QPixmap(48, 48)
        empty.set_image(pm)
        assert empty._pixmap_label is not None
        assert empty._svg_widget is None

    def test_restore_default_svg(self, qapp: QApplication) -> None:
        empty = TEmpty()
        pm = QPixmap(48, 48)
        empty.set_image(pm)
        assert empty._svg_widget is None
        empty.set_image(None)
        assert empty._svg_widget is not None
        assert empty._pixmap_label is None


class TestTEmptyExtra:
    """Tests for custom action area."""

    def test_set_extra_widget(self, qapp: QApplication) -> None:
        empty = TEmpty()
        btn = QLabel("Action")
        empty.set_extra(btn)
        assert empty._extra_widget is btn

    def test_replace_extra_widget(self, qapp: QApplication) -> None:
        empty = TEmpty()
        btn1 = QLabel("Action 1")
        btn2 = QLabel("Action 2")
        empty.set_extra(btn1)
        empty.set_extra(btn2)
        assert empty._extra_widget is btn2
