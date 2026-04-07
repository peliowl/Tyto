"""Property-based tests for Dark mode color consistency.

Covers Properties 40, 41, and 42 from the design document.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.core.theme_engine import ThemeEngine


# -- Helpers --


def _load_token_file(path: Path) -> dict:
    """Load raw JSON token data from file."""
    return json.loads(path.read_text(encoding="utf-8"))


# -- Fixtures --


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    """Reset ThemeEngine singleton between tests."""
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


# ---------------------------------------------------------------------------
# Property 40: Component Dark mode color consistency
# ---------------------------------------------------------------------------


class TestDarkModeColorConsistency:
    """Property 40: For any theme (light/dark), after switching,
    ThemeEngine.get_token() returns values matching the token file.

    **Validates: Requirements 25.5, 26.4, 27.3, 28.3, 29.1**
    """

    # Feature: tyto-ui-lib-v1, Property 40: 组件 Dark 模式颜色一致性
    @settings(max_examples=100)
    @given(theme_name=st.sampled_from(["light", "dark"]))
    def test_token_values_match_file(self, qapp: QApplication, theme_name: str) -> None:
        """For any theme name, get_token() returns values consistent with the JSON file."""
        engine = ThemeEngine.instance()
        engine.load_tokens()
        engine.switch_theme(theme_name)

        # Load the raw token file for comparison
        import importlib.resources

        tokens_dir = Path(str(importlib.resources.files("tyto_ui_lib") / "styles" / "tokens"))
        raw = _load_token_file(tokens_dir / f"{theme_name}.json")

        # Verify all color tokens match
        for key, expected in raw["colors"].items():
            actual = engine.get_token("colors", key)
            assert actual == expected, (
                f"Theme '{theme_name}', colors.{key}: expected {expected!r}, got {actual!r}"
            )

        # Verify all spacing tokens match
        for key, expected in raw["spacing"].items():
            actual = engine.get_token("spacing", key)
            assert actual == expected

        # Verify all radius tokens match
        for key, expected in raw["radius"].items():
            actual = engine.get_token("radius", key)
            assert actual == expected

        # Verify all font_sizes tokens match
        for key, expected in raw["font_sizes"].items():
            actual = engine.get_token("font_sizes", key)
            assert actual == expected

        # Verify all shadows tokens match
        for key, expected in raw["shadows"].items():
            actual = engine.get_token("shadows", key)
            assert actual == expected


# ---------------------------------------------------------------------------
# Property 41: Switch track repaint responds to theme switch
# ---------------------------------------------------------------------------


class TestSwitchTrackRepaint:
    """Property 41: TSwitch track repaints after theme switch,
    ensuring _track.update() is called.

    **Validates: Requirements 27.1, 27.2, 27.3**
    """

    # Feature: tyto-ui-lib-v1, Property 41: Switch 轨道重绘响应主题切换
    @settings(max_examples=100)
    @given(
        initial_theme=st.sampled_from(["light", "dark"]),
        target_theme=st.sampled_from(["light", "dark"]),
    )
    def test_track_update_called_on_theme_switch(
        self, qapp: QApplication, initial_theme: str, target_theme: str
    ) -> None:
        """For any theme transition, TSwitch.apply_theme() triggers _track.update()."""
        from unittest.mock import patch

        from tyto_ui_lib.components.atoms.switch import TSwitch

        engine = ThemeEngine.instance()
        engine.load_tokens()
        engine.switch_theme(initial_theme)

        sw = TSwitch(checked=False)

        # Patch _track.update to detect the call
        with patch.object(sw._track, "update", wraps=sw._track.update) as mock_update:
            engine.switch_theme(target_theme)
            # apply_theme is called via theme_changed signal, which calls _track.update()
            mock_update.assert_called()


# ---------------------------------------------------------------------------
# Property 42: Gallery interface Dark mode background color
# ---------------------------------------------------------------------------


class TestGalleryDarkModeBackground:
    """Property 42: Gallery interface elements use correct background
    colors from tokens after theme switch.

    **Validates: Requirements 30.1, 30.5, 30.6, 30.8**
    """

    # Feature: tyto-ui-lib-v1, Property 42: Gallery 界面 Dark 模式背景色
    @settings(max_examples=100)
    @given(theme_name=st.sampled_from(["light", "dark"]))
    def test_gallery_styles_use_token_colors(self, qapp: QApplication, theme_name: str) -> None:
        """For any theme, GalleryStyles methods return QSS containing the correct token values."""
        import sys

        # Ensure examples package is importable
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

        from examples.gallery.styles.gallery_styles import GalleryStyles

        engine = ThemeEngine.instance()
        engine.load_tokens()
        engine.switch_theme(theme_name)

        tokens = engine.current_tokens()
        assert tokens is not None

        bg_default = tokens.colors["bg_default"]
        bg_elevated = tokens.colors["bg_elevated"]
        text_primary = tokens.colors["text_primary"]
        border = tokens.colors["border"]

        # Main window style should contain bg_default
        main_style = GalleryStyles.main_window_style(theme_name)
        assert bg_default in main_style, (
            f"Theme '{theme_name}': main_window_style missing bg_default '{bg_default}'"
        )

        # Showcase panel style should contain bg_default
        showcase_style = GalleryStyles.showcase_panel_style(theme_name)
        assert bg_default in showcase_style, (
            f"Theme '{theme_name}': showcase_panel_style missing bg_default '{bg_default}'"
        )

        # Nav menu style should contain bg_elevated and border
        nav_style = GalleryStyles.nav_menu_style(theme_name)
        assert bg_elevated in nav_style, (
            f"Theme '{theme_name}': nav_menu_style missing bg_elevated '{bg_elevated}'"
        )
        assert border in nav_style, (
            f"Theme '{theme_name}': nav_menu_style missing border '{border}'"
        )

        # Top bar style should contain bg_elevated and text_primary
        top_style = GalleryStyles.top_bar_style(theme_name)
        assert bg_elevated in top_style, (
            f"Theme '{theme_name}': top_bar_style missing bg_elevated '{bg_elevated}'"
        )
        assert text_primary in top_style, (
            f"Theme '{theme_name}': top_bar_style missing text_primary '{text_primary}'"
        )
