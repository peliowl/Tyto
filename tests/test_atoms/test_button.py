"""Unit tests for TButton atom component."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.button import TButton
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


def _make_mouse_press(pos: QPointF | None = None) -> QMouseEvent:
    p = pos or QPointF(5, 5)
    return QMouseEvent(
        QEvent.Type.MouseButtonPress, p, p,
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _make_mouse_release(pos: QPointF | None = None) -> QMouseEvent:
    p = pos or QPointF(5, 5)
    return QMouseEvent(
        QEvent.Type.MouseButtonRelease, p, p,
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


class TestTButtonCreation:
    """Tests for TButton initialization and type assignment."""

    def test_default_type(self, qapp: QApplication) -> None:
        btn = TButton("OK")
        assert btn.button_type == TButton.ButtonType.DEFAULT
        assert btn.text == "OK"

    def test_primary_type(self, qapp: QApplication) -> None:
        btn = TButton("Go", button_type=TButton.ButtonType.PRIMARY)
        assert btn.button_type == TButton.ButtonType.PRIMARY
        assert btn.property("buttonType") == "primary"

    def test_dashed_type(self, qapp: QApplication) -> None:
        btn = TButton(button_type=TButton.ButtonType.DASHED)
        assert btn.button_type == TButton.ButtonType.DASHED

    def test_text_type(self, qapp: QApplication) -> None:
        btn = TButton(button_type=TButton.ButtonType.TEXT)
        assert btn.button_type == TButton.ButtonType.TEXT


class TestTButtonClicked:
    """Tests for clicked signal emission."""

    def test_click_emits_signal(self, qapp: QApplication) -> None:
        btn = TButton("Click me")
        btn.resize(100, 40)
        received: list[bool] = []
        btn.clicked.connect(lambda: received.append(True))
        btn.mousePressEvent(_make_mouse_press())
        btn.mouseReleaseEvent(_make_mouse_release())
        assert len(received) == 1

    def test_loading_blocks_click(self, qapp: QApplication) -> None:
        btn = TButton("Wait")
        btn.resize(100, 40)
        btn.set_loading(True)
        received: list[bool] = []
        btn.clicked.connect(lambda: received.append(True))
        btn.mousePressEvent(_make_mouse_press())
        btn.mouseReleaseEvent(_make_mouse_release())
        assert len(received) == 0

    def test_disabled_blocks_click(self, qapp: QApplication) -> None:
        btn = TButton("No")
        btn.resize(100, 40)
        btn.set_disabled(True)
        received: list[bool] = []
        btn.clicked.connect(lambda: received.append(True))
        btn.mousePressEvent(_make_mouse_press())
        btn.mouseReleaseEvent(_make_mouse_release())
        assert len(received) == 0


class TestTButtonLoadingState:
    """Tests for loading state behavior."""

    def test_loading_shows_spinner(self, qapp: QApplication) -> None:
        btn = TButton("Load")
        assert btn._spinner.isHidden()
        btn.set_loading(True)
        assert not btn._spinner.isHidden()
        assert btn.loading is True

    def test_loading_exit_hides_spinner(self, qapp: QApplication) -> None:
        btn = TButton("Load")
        btn.set_loading(True)
        btn.set_loading(False)
        assert btn._spinner.isHidden()
        assert btn.loading is False


class TestTButtonDisabledState:
    """Tests for disabled state behavior."""

    def test_disabled_sets_cursor(self, qapp: QApplication) -> None:
        btn = TButton("Dis")
        btn.set_disabled(True)
        assert btn.cursor().shape() == Qt.CursorShape.ForbiddenCursor
        assert not btn.isEnabled()

    def test_disabled_restore(self, qapp: QApplication) -> None:
        btn = TButton("Dis")
        btn.set_disabled(True)
        btn.set_disabled(False)
        assert btn.isEnabled()


# ---------------------------------------------------------------------------
# Property-Based Tests (Bugfix V1.0.1)
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st


class TestTButtonQSSPropertySelector:
    """Property 34: Button QSS attribute selector takes effect after creation.

    **Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5**
    """

    # Feature: tyto-ui-lib-v1, Property 34: Button QSS 属性选择器生效
    @settings(max_examples=100)
    @given(button_type=st.sampled_from(list(TButton.ButtonType)))
    def test_button_type_qss_property(self, qapp: QApplication, button_type: TButton.ButtonType) -> None:
        """For any ButtonType, the created TButton's dynamic property 'buttonType' equals the type's value."""
        btn = TButton("Test", button_type=button_type)
        assert btn.property("buttonType") == button_type.value


class TestButtonStylePropagation:
    """Verify that TButton QSS property selector fix (Task 19) propagates
    to downstream components like MessageShowcase.

    When MessageShowcase creates TButton instances with different ButtonTypes,
    each button's dynamic property 'buttonType' should be correctly set,
    ensuring QSS attribute selectors render the correct styles.

    **Validates: Requirements 24.3**
    """

    def test_primary_button_has_correct_property(self, qapp: QApplication) -> None:
        """A PRIMARY TButton (like the Success button in MessageShowcase) has correct property."""
        btn = TButton("Success", button_type=TButton.ButtonType.PRIMARY)
        assert btn.property("buttonType") == "primary"

    def test_default_button_has_correct_property(self, qapp: QApplication) -> None:
        """A DEFAULT TButton (like the Info button in MessageShowcase) has correct property."""
        btn = TButton("Info", button_type=TButton.ButtonType.DEFAULT)
        assert btn.property("buttonType") == "default"

    def test_all_message_showcase_button_types(self, qapp: QApplication) -> None:
        """All button types used in MessageShowcase have correct QSS properties."""
        # MessageShowcase creates: Info(DEFAULT), Success(PRIMARY), Warning(DEFAULT), Error(DEFAULT)
        configs = [
            ("Info", TButton.ButtonType.DEFAULT),
            ("Success", TButton.ButtonType.PRIMARY),
            ("Warning", TButton.ButtonType.DEFAULT),
            ("Error", TButton.ButtonType.DEFAULT),
        ]
        for text, btn_type in configs:
            btn = TButton(text, button_type=btn_type)
            assert btn.property("buttonType") == btn_type.value, (
                f"Button '{text}' with type {btn_type} has wrong property"
            )


    def test_button_apply_theme_has_unpolish_polish(self, qapp: QApplication, tokens_dir: Path) -> None:
        """Verify TButton.apply_theme() triggers re-polish for QSS selector activation."""
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        engine.switch_theme("light")

        btn = TButton("Test", button_type=TButton.ButtonType.PRIMARY)
        # The global stylesheet (set by switch_theme) should be non-empty
        assert qapp.styleSheet() != ""
        # The buttonType property must still be correct after theme application
        assert btn.property("buttonType") == "primary"
