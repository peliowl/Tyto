"""Unit tests for ThemeEngine singleton."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.core.theme_engine import ThemeEngine


def _make_valid_token_data(name: str) -> dict:
    """Return a minimal valid token dictionary."""
    return {
        "name": name,
        "colors": {
            "primary": "#18a058" if name == "light" else "#63e2b7",
            "primary_hover": "#36ad6a",
            "primary_pressed": "#0c7a43",
            "success": "#18a058",
            "warning": "#f0a020",
            "error": "#d03050",
            "info": "#2080f0",
            "info_hover": "#4098fc",
            "info_pressed": "#1060c9",
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


@pytest.fixture()
def templates_dir(tmp_path: Path) -> Path:
    """Create a temp directory with a simple QSS template."""
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    (tpl_dir / "test.qss.j2").write_text(
        "QWidget { color: {{ colors.primary }}; padding: {{ spacing.medium }}px; }",
        encoding="utf-8",
    )
    return tpl_dir


class TestThemeEngineSingleton:
    """Tests for singleton behaviour."""

    def test_instance_returns_same_object(self, qapp: QApplication) -> None:
        a = ThemeEngine.instance()
        b = ThemeEngine.instance()
        assert a is b

    def test_reset_creates_new_instance(self, qapp: QApplication) -> None:
        a = ThemeEngine.instance()
        ThemeEngine.reset()
        b = ThemeEngine.instance()
        assert a is not b


class TestThemeEngineLoadAndSwitch:
    """Tests for loading tokens and switching themes."""

    def test_load_tokens_from_directory(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        assert "light" in engine._themes
        assert "dark" in engine._themes

    def test_switch_theme(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        engine.switch_theme("light")
        assert engine.current_theme() == "light"

    def test_switch_unknown_theme_raises(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        with pytest.raises(ValueError, match="Unknown theme"):
            engine.switch_theme("nope")

    def test_get_token(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        engine.switch_theme("light")
        assert engine.get_token("colors", "primary") == "#18a058"
        assert engine.get_token("spacing", "medium") == 8

    def test_get_token_no_active_theme_raises(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        with pytest.raises(RuntimeError, match="No active theme"):
            engine.get_token("colors", "primary")

    def test_theme_changed_signal(self, qapp: QApplication, tokens_dir: Path) -> None:
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        received: list[str] = []
        engine.theme_changed.connect(received.append)
        engine.switch_theme("dark")
        assert received == ["dark"]

    def test_load_nonexistent_dir_raises(self, qapp: QApplication) -> None:
        engine = ThemeEngine.instance()
        with pytest.raises(FileNotFoundError):
            engine.load_tokens("/nonexistent/dir")


class TestThemeEngineRenderQSS:
    """Tests for Jinja2 QSS rendering."""

    def test_render_qss_contains_token_values(
        self, qapp: QApplication, tokens_dir: Path, templates_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Monkeypatch the default templates dir to use our fixture
        monkeypatch.setattr(
            "tyto_ui_lib.core.theme_engine._default_templates_dir",
            lambda: templates_dir,
        )
        engine = ThemeEngine.instance()
        engine.load_tokens(tokens_dir)
        engine.switch_theme("light")
        qss = engine.render_qss("test.qss.j2")
        assert "#18a058" in qss
        assert "8px" in qss

    def test_render_qss_no_env_raises(self, qapp: QApplication) -> None:
        engine = ThemeEngine.instance()
        with pytest.raises(RuntimeError, match="Jinja2 environment not initialised"):
            engine.render_qss("test.qss.j2")
