"""Unit tests for BaseWidget base class."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


def _make_valid_token_data(name: str) -> dict:
    """Return a minimal valid token dictionary."""
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
    """Reset ThemeEngine singleton between tests."""
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


@pytest.fixture()
def tokens_dir(tmp_path: Path) -> Path:
    """Create a temp directory with light and dark token files."""
    for name in ("light", "dark"):
        fp = tmp_path / f"{name}.json"
        fp.write_text(json.dumps(_make_valid_token_data(name)), encoding="utf-8")
    return tmp_path


class TestBaseWidgetLifecycle:
    """Tests for BaseWidget initialization and cleanup."""

    def test_connects_to_theme_changed(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)

        calls: list[str] = []

        class TestWidget(BaseWidget):
            def apply_theme(self) -> None:
                calls.append("applied")

        widget = TestWidget()
        engine.switch_theme("light")
        assert "applied" in calls

    def test_cleanup_disconnects_signal(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        engine.switch_theme("light")

        calls: list[str] = []

        class TestWidget(BaseWidget):
            def apply_theme(self) -> None:
                calls.append("applied")

        widget = TestWidget()
        calls.clear()
        widget.cleanup()

        engine.switch_theme("dark")
        assert calls == []

    def test_cleanup_idempotent(self, qapp: QApplication) -> None:
        widget = BaseWidget()
        widget.cleanup()
        widget.cleanup()  # Should not raise

    def test_apply_theme_called_if_theme_active(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        engine.switch_theme("light")

        calls: list[str] = []

        class TestWidget(BaseWidget):
            def apply_theme(self) -> None:
                calls.append("applied")

        _widget = TestWidget()
        assert "applied" in calls

    def test_apply_theme_not_called_if_no_theme(self, qapp: QApplication) -> None:
        calls: list[str] = []

        class TestWidget(BaseWidget):
            def apply_theme(self) -> None:
                calls.append("applied")

        _widget = TestWidget()
        assert calls == []
