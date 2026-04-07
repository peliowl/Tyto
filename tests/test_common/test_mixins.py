"""Unit tests for behavior mixins (HoverEffect, ClickRipple, FocusGlow, Disabled)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QEnterEvent, QFocusEvent, QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.click_ripple import ClickRippleMixin
from tyto_ui_lib.common.traits.disabled import DisabledMixin
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


def _make_valid_token_data(name: str) -> dict:
    return {
        "name": name,
        "colors": {
            "primary": "#18a058",
            "primary_hover": "#36ad6a",
            "primary_pressed": "#0c7a43",
            "success": "#18a058",
            "warning": "#f0a020",
            "error": "#d03050",
            "info": "#2080f0",
            "bg_default": "#ffffff",
            "bg_elevated": "#f8f8fa",
            "text_primary": "#333639",
            "text_secondary": "#667085",
            "text_disabled": "#c2c2c2",
            "border": "#e0e0e6",
            "border_focus": "#18a058",
            "white": "#ffffff",
            "mask": "rgba(0, 0, 0, 0.4)",
        },
        "spacing": {"small": 4, "medium": 8, "large": 16, "xlarge": 24},
        "radius": {"small": 2, "medium": 4, "large": 8},
        "font_sizes": {"small": 12, "medium": 14, "large": 16, "xlarge": 20},
        "shadows": {
            "small": "0 2px 8px rgba(0,0,0,0.08)",
            "medium": "0 4px 16px rgba(0,0,0,0.12)",
            "large": "0 8px 32px rgba(0,0,0,0.16)",
        },
    }


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


@pytest.fixture()
def tokens_dir(tmp_path: Path) -> Path:
    for name in ("light", "dark"):
        fp = tmp_path / f"{name}.json"
        fp.write_text(json.dumps(_make_valid_token_data(name)), encoding="utf-8")
    return tmp_path


# -- Test widget classes combining mixins with BaseWidget --

class HoverWidget(HoverEffectMixin, BaseWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_hover_effect()


class ClickWidget(ClickRippleMixin, BaseWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_click_ripple()


class FocusWidget(FocusGlowMixin, BaseWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_focus_glow()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


class DisabledWidget(DisabledMixin, BaseWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_disabled()


class MultiMixinWidget(HoverEffectMixin, ClickRippleMixin, FocusGlowMixin, BaseWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_hover_effect()
        self._init_click_ripple()
        self._init_focus_glow()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


def _make_enter_event() -> QEnterEvent:
    return QEnterEvent(QPointF(5, 5), QPointF(5, 5), QPointF(5, 5))


def _make_leave_event() -> QEvent:
    return QEvent(QEvent.Type.Leave)


def _make_mouse_press() -> QMouseEvent:
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(5, 5),
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _make_mouse_release() -> QMouseEvent:
    return QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        QPointF(5, 5),
        QPointF(5, 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _make_focus_in() -> QFocusEvent:
    return QFocusEvent(QEvent.Type.FocusIn, Qt.FocusReason.TabFocusReason)


def _make_focus_out() -> QFocusEvent:
    return QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.TabFocusReason)


class TestHoverEffectMixin:
    def test_cursor_changes_to_pointing_hand_on_enter(self, qapp: QApplication) -> None:
        w = HoverWidget()
        w.enterEvent(_make_enter_event())
        assert w.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_cursor_restores_on_leave(self, qapp: QApplication) -> None:
        w = HoverWidget()
        original = w.cursor().shape()
        w.enterEvent(_make_enter_event())
        w.leaveEvent(_make_leave_event())
        assert w.cursor().shape() == original


class TestClickRippleMixin:
    def test_pressed_property_set_on_press(self, qapp: QApplication) -> None:
        w = ClickWidget()
        w.mousePressEvent(_make_mouse_press())
        assert w.property("pressed") == True  # noqa: E712

    def test_pressed_property_cleared_on_release(self, qapp: QApplication) -> None:
        w = ClickWidget()
        w.mousePressEvent(_make_mouse_press())
        w.mouseReleaseEvent(_make_mouse_release())
        assert w.property("pressed") == False  # noqa: E712


class TestFocusGlowMixin:
    def test_focused_property_set_on_focus_in(self, qapp: QApplication) -> None:
        w = FocusWidget()
        w.focusInEvent(_make_focus_in())
        assert w.property("focused") == True  # noqa: E712

    def test_focused_property_cleared_on_focus_out(self, qapp: QApplication) -> None:
        w = FocusWidget()
        w.focusInEvent(_make_focus_in())
        w.focusOutEvent(_make_focus_out())
        assert w.property("focused") == False  # noqa: E712


class TestDisabledMixin:
    def test_disabled_sets_forbidden_cursor(self, qapp: QApplication) -> None:
        w = DisabledWidget()
        w.set_disabled_style(True)
        assert w.cursor().shape() == Qt.CursorShape.ForbiddenCursor
        assert not w.isEnabled()

    def test_disabled_restores_on_enable(self, qapp: QApplication) -> None:
        w = DisabledWidget()
        w.set_disabled_style(True)
        w.set_disabled_style(False)
        assert w.isEnabled()
        assert w.cursor().shape() != Qt.CursorShape.ForbiddenCursor


class TestMultiMixinNoConflict:
    def test_all_mixins_work_together(self, qapp: QApplication) -> None:
        w = MultiMixinWidget()
        # Hover
        w.enterEvent(_make_enter_event())
        assert w.cursor().shape() == Qt.CursorShape.PointingHandCursor
        # Press
        w.mousePressEvent(_make_mouse_press())
        assert w.property("pressed") == True  # noqa: E712
        # Focus
        w.focusInEvent(_make_focus_in())
        assert w.property("focused") == True  # noqa: E712
        # Release and leave
        w.mouseReleaseEvent(_make_mouse_release())
        assert w.property("pressed") == False  # noqa: E712
        w.focusOutEvent(_make_focus_out())
        assert w.property("focused") == False  # noqa: E712
        w.leaveEvent(_make_leave_event())
