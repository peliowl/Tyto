"""Unit tests for TInputGroup molecule component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from tyto_ui_lib.components.molecules.inputgroup import TInputGroup
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTInputGroupCreation:
    """Tests for TInputGroup initialization."""

    def test_default_empty(self, qapp: QApplication) -> None:
        group = TInputGroup()
        assert len(group._children) == 0


class TestTInputGroupAddRemove:
    """Tests for add/insert/remove operations."""

    def test_add_widget(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QWidget()
        w2 = QWidget()
        group.add_widget(w1)
        group.add_widget(w2)
        assert len(group._children) == 2

    def test_insert_widget(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QWidget()
        w2 = QWidget()
        w3 = QWidget()
        group.add_widget(w1)
        group.add_widget(w3)
        group.insert_widget(1, w2)
        assert group._children == [w1, w2, w3]

    def test_remove_widget(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QWidget()
        w2 = QWidget()
        group.add_widget(w1)
        group.add_widget(w2)
        group.remove_widget(w1)
        assert group._children == [w2]


class TestTInputGroupRadius:
    """Tests for border-radius merging invariant."""

    def test_two_children_radius(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QPushButton("A")
        w2 = QPushButton("B")
        group.add_widget(w1)
        group.add_widget(w2)
        assert w1.property("groupPosition") == "first"
        assert w2.property("groupPosition") == "last"

    def test_three_children_radius(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QPushButton("A")
        w2 = QPushButton("B")
        w3 = QPushButton("C")
        group.add_widget(w1)
        group.add_widget(w2)
        group.add_widget(w3)
        assert w1.property("groupPosition") == "first"
        assert w2.property("groupPosition") == "middle"
        assert w3.property("groupPosition") == "last"

    def test_single_child_solo(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QPushButton("A")
        group.add_widget(w1)
        assert w1.property("groupPosition") == "solo"

    def test_radius_recalculated_after_remove(self, qapp: QApplication) -> None:
        group = TInputGroup()
        w1 = QPushButton("A")
        w2 = QPushButton("B")
        w3 = QPushButton("C")
        group.add_widget(w1)
        group.add_widget(w2)
        group.add_widget(w3)
        group.remove_widget(w2)
        assert w1.property("groupPosition") == "first"
        assert w3.property("groupPosition") == "last"
