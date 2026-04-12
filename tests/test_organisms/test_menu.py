"""Unit tests for TMenu, TMenuItem, and TMenuItemGroup organism components."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QWidget

from tyto_ui_lib.components.organisms.menu import TMenu, TMenuItem, TMenuItemGroup
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


def _make_click(x: int = 5, y: int = 5) -> QMouseEvent:
    """Create a left-button mouse press event at (x, y)."""
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPoint(x, y),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


class TestTMenuItem:
    """Tests for TMenuItem."""

    def test_key_and_label(self, qapp: QApplication) -> None:
        item = TMenuItem(key="home", label="Home")
        assert item.key == "home"
        assert item.label == "Home"

    def test_active_state_roundtrip(self, qapp: QApplication) -> None:
        item = TMenuItem(key="k1", label="K1")
        assert item.is_active() is False
        item.set_active(True)
        assert item.is_active() is True
        assert item.property("active") == "true"
        item.set_active(False)
        assert item.is_active() is False
        assert item.property("active") == "false"

    def test_disabled_cursor(self, qapp: QApplication) -> None:
        item = TMenuItem(key="d", label="D", disabled=True)
        assert item.disabled is True
        assert item.cursor().shape() == Qt.CursorShape.ForbiddenCursor

    def test_clicked_signal(self, qapp: QApplication, qtbot: object) -> None:
        from pytestqt.qtbot import QtBot

        assert isinstance(qtbot, QtBot)
        item = TMenuItem(key="sig", label="Sig")
        with qtbot.waitSignal(item.clicked, timeout=1000) as blocker:
            item.mousePressEvent(_make_click())
        assert blocker.args == ["sig"]

    def test_disabled_no_signal(self, qapp: QApplication) -> None:
        item = TMenuItem(key="dis", label="Dis", disabled=True)
        signals: list[str] = []
        item.clicked.connect(lambda k: signals.append(k))
        item.mousePressEvent(_make_click())
        assert signals == []


class TestTMenuItemGroup:
    """Tests for TMenuItemGroup."""

    def test_key_and_label(self, qapp: QApplication) -> None:
        group = TMenuItemGroup(key="grp", label="Group")
        assert group.key == "grp"
        assert group.label == "Group"

    def test_expanded_default(self, qapp: QApplication) -> None:
        group = TMenuItemGroup(key="g", expanded=True)
        assert group.is_expanded() is True

    def test_collapsed_default(self, qapp: QApplication) -> None:
        group = TMenuItemGroup(key="g", expanded=False)
        assert group.is_expanded() is False

    def test_set_expanded_roundtrip(self, qapp: QApplication, qtbot: object) -> None:
        from pytestqt.qtbot import QtBot

        assert isinstance(qtbot, QtBot)
        group = TMenuItemGroup(key="g", expanded=True)
        with qtbot.waitSignal(group.expanded_changed, timeout=1000):
            group.set_expanded(False, animate=False)
        assert group.is_expanded() is False
        with qtbot.waitSignal(group.expanded_changed, timeout=1000):
            group.set_expanded(True, animate=False)
        assert group.is_expanded() is True

    def test_add_item(self, qapp: QApplication) -> None:
        group = TMenuItemGroup(key="g", label="G")
        group.add_item(TMenuItem(key="a", label="A"))
        group.add_item(TMenuItem(key="b", label="B"))
        items = group.get_items()
        assert len(items) == 2
        assert items[0].key == "a"
        assert items[1].key == "b"

    def test_get_all_item_keys(self, qapp: QApplication) -> None:
        group = TMenuItemGroup(key="g", label="G")
        group.add_item(TMenuItem(key="a", label="A"))
        sub = TMenuItemGroup(key="sub", label="Sub")
        sub.add_item(TMenuItem(key="b", label="B"))
        group.add_item(sub)
        keys = group.get_all_item_keys()
        assert "a" in keys
        assert "sub" in keys
        assert "b" in keys


class TestTMenu:
    """Tests for TMenu."""

    def test_mode_property(self, qapp: QApplication) -> None:
        menu_v = TMenu(mode=TMenu.MenuMode.VERTICAL)
        assert menu_v.mode == TMenu.MenuMode.VERTICAL
        menu_h = TMenu(mode=TMenu.MenuMode.HORIZONTAL)
        assert menu_h.mode == TMenu.MenuMode.HORIZONTAL

    def test_active_key_roundtrip(self, qapp: QApplication) -> None:
        menu = TMenu()
        menu.add_item(TMenuItem(key="a", label="A"))
        menu.add_item(TMenuItem(key="b", label="B"))
        menu.set_active_key("b")
        assert menu.get_active_key() == "b"

    def test_item_selected_signal(self, qapp: QApplication, qtbot: object) -> None:
        from pytestqt.qtbot import QtBot

        assert isinstance(qtbot, QtBot)
        menu = TMenu()
        item = TMenuItem(key="x", label="X")
        menu.add_item(item)
        with qtbot.waitSignal(menu.item_selected, timeout=1000) as blocker:
            item.mousePressEvent(_make_click())
        assert blocker.args == ["x"]

    def test_disabled_blocks_signal(self, qapp: QApplication) -> None:
        menu = TMenu(disabled=True)
        item = TMenuItem(key="y", label="Y")
        menu.add_item(item)
        signals: list[str] = []
        menu.item_selected.connect(lambda k: signals.append(k))
        item.mousePressEvent(_make_click())
        assert signals == []

    def test_route_awareness(self, qapp: QApplication) -> None:
        menu = TMenu(route_awareness=True)
        menu.add_item(TMenuItem(key="/home", label="Home"))
        menu.add_item(TMenuItem(key="/settings", label="Settings"))
        menu.set_route("/settings/profile")
        assert menu.get_active_key() == "/settings"

    def test_route_awareness_disabled(self, qapp: QApplication) -> None:
        menu = TMenu(route_awareness=False)
        menu.add_item(TMenuItem(key="/home", label="Home"))
        menu.set_route("/home")
        assert menu.get_active_key() == ""

    def test_route_no_match_keeps_current(self, qapp: QApplication) -> None:
        menu = TMenu(route_awareness=True)
        menu.add_item(TMenuItem(key="/home", label="Home"))
        menu.set_active_key("/home")
        menu.set_route("/unknown")
        assert menu.get_active_key() == "/home"

    def test_collapsed_mode(self, qapp: QApplication) -> None:
        menu = TMenu()
        menu.add_item(TMenuItem(key="a", label="A"))
        assert menu.collapsed is False
        menu.set_collapsed(True)
        assert menu.collapsed is True
        menu.set_collapsed(False)
        assert menu.collapsed is False

    def test_nested_group_signal(self, qapp: QApplication, qtbot: object) -> None:
        from pytestqt.qtbot import QtBot

        assert isinstance(qtbot, QtBot)
        menu = TMenu()
        group = TMenuItemGroup(key="g", label="G")
        child = TMenuItem(key="child", label="Child")
        group.add_item(child)
        menu.add_item(group)
        with qtbot.waitSignal(menu.item_selected, timeout=1000) as blocker:
            child.mousePressEvent(_make_click())
        assert blocker.args == ["child"]


class TestPopupEventFilter:
    """Tests for popup eventFilter under the new layered structure."""

    def _create_horizontal_group(self) -> TMenuItemGroup:
        """Create a TMenuItemGroup in horizontal mode with a child item."""
        group = TMenuItemGroup(key="g", label="G")
        group.add_item(TMenuItem(key="a", label="A"))
        group.set_menu_mode(TMenu.MenuMode.HORIZONTAL)
        return group

    def test_event_filter_installed_on_popup_and_container(self, qapp: QApplication) -> None:
        """Verify eventFilter is installed on both popup and container."""
        group = self._create_horizontal_group()
        popup = group._create_popup()
        try:
            container = popup.findChild(QWidget, "menu_popup_container")
            assert container is not None
            # Verify the filter is active by sending a synthetic Enter event
            # on the container and checking the timer is stopped.
            from PySide6.QtCore import QTimer

            group._popup = popup
            group._hide_timer = QTimer(group)
            group._hide_timer.setSingleShot(True)
            group._hide_timer.setInterval(200)
            group._hide_timer.start()
            assert group._hide_timer.isActive()

            enter_event = QEvent(QEvent.Type.Enter)
            group.eventFilter(container, enter_event)
            assert not group._hide_timer.isActive()
        finally:
            popup.close()
            popup.deleteLater()

    def test_enter_on_container_cancels_hide(self, qapp: QApplication) -> None:
        """Mouse entering the container should cancel the hide timer."""
        group = self._create_horizontal_group()
        popup = group._create_popup()
        try:
            from PySide6.QtCore import QTimer

            group._popup = popup
            group._hide_timer = QTimer(group)
            group._hide_timer.setSingleShot(True)
            group._hide_timer.setInterval(200)
            group._hide_timer.start()

            container = popup.findChild(QWidget, "menu_popup_container")
            enter_event = QEvent(QEvent.Type.Enter)
            group.eventFilter(container, enter_event)
            assert not group._hide_timer.isActive()
        finally:
            popup.close()
            popup.deleteLater()

    def test_leave_on_container_starts_hide(self, qapp: QApplication) -> None:
        """Mouse leaving the container should start the hide timer."""
        group = self._create_horizontal_group()
        popup = group._create_popup()
        try:
            group._popup = popup
            container = popup.findChild(QWidget, "menu_popup_container")
            leave_event = QEvent(QEvent.Type.Leave)
            group.eventFilter(container, leave_event)
            assert group._hide_timer is not None
            assert group._hide_timer.isActive()
        finally:
            popup.close()
            popup.deleteLater()

    def test_do_hide_popup_checks_container(self, qapp: QApplication) -> None:
        """_do_hide_popup should not hide if container reports underMouse."""
        from unittest.mock import patch

        group = self._create_horizontal_group()
        popup = group._create_popup()
        try:
            group._popup = popup
            popup.show()
            container = popup.findChild(QWidget, "menu_popup_container")
            assert container is not None

            # popup.underMouse() = False, container.underMouse() = True -> stay visible
            with (
                patch.object(popup, "underMouse", return_value=False),
                patch.object(container, "underMouse", return_value=True),
            ):
                group._do_hide_popup()
                assert popup.isVisible()

            # Both return False -> popup should hide
            with (
                patch.object(popup, "underMouse", return_value=False),
                patch.object(container, "underMouse", return_value=False),
            ):
                group._do_hide_popup()
                assert not popup.isVisible()
        finally:
            popup.close()
            popup.deleteLater()
