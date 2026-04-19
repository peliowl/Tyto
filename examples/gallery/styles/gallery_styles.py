"""Theme-aware style helpers for the Gallery application.

These styles are specific to the Gallery chrome (navigation, top bar,
section headings) and are *not* part of the Tyto component library itself.
Values are derived from the active ThemeEngine tokens where possible.
"""

from __future__ import annotations

from tyto_ui_lib import ThemeEngine


class GalleryStyles:
    """Gallery-specific QSS style provider, theme-aware.

    All methods are static and read the current theme from
    :class:`ThemeEngine` so that styles update automatically on
    theme switches.
    """

    @staticmethod
    def _tokens() -> dict[str, str | int]:
        """Collect commonly used token values from the active theme."""
        engine = ThemeEngine.instance()
        t = engine.current_tokens()
        if t is None:
            return {}
        return {
            "bg_default": t.colors.get("bg_default", "#ffffff"),
            "bg_elevated": t.colors.get("bg_elevated", "#f8f8fa"),
            "text_primary": t.colors.get("text_primary", "#333639"),
            "text_secondary": t.colors.get("text_secondary", "#667085"),
            "border": t.colors.get("border", "#e0e0e6"),
            "primary": t.colors.get("primary", "#18a058"),
            "primary_hover": t.colors.get("primary_hover", "#36ad6a"),
            "font_small": t.font_sizes.get("small", 12),
            "font_medium": t.font_sizes.get("medium", 14),
            "font_large": t.font_sizes.get("large", 16),
            "font_xlarge": t.font_sizes.get("xlarge", 20),
            "spacing_small": t.spacing.get("small", 4),
            "spacing_medium": t.spacing.get("medium", 8),
            "spacing_large": t.spacing.get("large", 16),
            "spacing_xlarge": t.spacing.get("xlarge", 24),
        }

    @staticmethod
    def nav_menu_style(theme: str) -> str:
        """Return QSS for the left navigation menu.

        Args:
            theme: ``"light"`` or ``"dark"``.
        """
        tk = GalleryStyles._tokens()
        if not tk:
            return ""
        return (
            f"QWidget#nav_menu {{"
            f"  background-color: {tk['bg_elevated']};"
            f"  border-right: 1px solid {tk['border']};"
            f"}}"
            f"QScrollArea#nav_scroll_area {{"
            f"  background-color: {tk['bg_elevated']};"
            f"  border: none;"
            f"}}"
            f"QWidget#nav_scroll_content {{"
            f"  background-color: {tk['bg_elevated']};"
            f"}}"
            f"QPushButton.nav_item {{"
            f"  text-align: left;"
            f"  border: none;"
            f"  padding: {tk['spacing_medium']}px {tk['spacing_large']}px;"
            f"  font-size: {tk['font_medium']}px;"
            f"  color: {tk['text_primary']};"
            f"  background: transparent;"
            f"}}"
            f"QPushButton.nav_item:hover {{"
            f"  background-color: {tk['border']};"
            f"}}"
            f"QPushButton.nav_item[active=\"true\"] {{"
            f"  color: {tk['primary']};"
            f"  font-weight: bold;"
            f"}}"
            f"QLabel.nav_category {{"
            f"  font-size: {tk['font_small']}px;"
            f"  font-weight: bold;"
            f"  color: {tk['text_secondary']};"
            f"  padding: {tk['spacing_large']}px {tk['spacing_large']}px {tk['spacing_small']}px;"
            f"  text-transform: uppercase;"
            f"}}"
        )

    @staticmethod
    def top_bar_style(theme: str) -> str:
        """Return QSS for the top bar.

        Args:
            theme: ``"light"`` or ``"dark"``.
        """
        tk = GalleryStyles._tokens()
        if not tk:
            return ""
        return (
            f"QWidget#top_bar {{"
            f"  background-color: {tk['bg_elevated']};"
            f"  border-bottom: 1px solid {tk['border']};"
            f"}}"
            f"QWidget#top_bar QLabel {{"
            f"  color: {tk['text_primary']};"
            f"}}"
            f"QLabel#top_bar_title {{"
            f"  font-size: {tk['font_xlarge']}px;"
            f"  font-weight: bold;"
            f"  color: {tk['text_primary']};"
            f"}}"
        )

    @staticmethod
    def main_window_style(theme: str) -> str:
        """Return QSS for the main gallery window background.

        Args:
            theme: ``"light"`` or ``"dark"``.
        """
        tk = GalleryStyles._tokens()
        if not tk:
            return ""
        return (
            f"GalleryWindow {{"
            f"  background-color: {tk['bg_default']};"
            f"}}"
        )

    @staticmethod
    def showcase_panel_style(theme: str) -> str:
        """Return QSS for the showcase panel background.

        Args:
            theme: ``"light"`` or ``"dark"``.
        """
        tk = GalleryStyles._tokens()
        if not tk:
            return ""
        return (
            f"QScrollArea {{"
            f"  background-color: {tk['bg_default']};"
            f"  border: none;"
            f"}}"
            f"QScrollArea > QWidget > QWidget {{"
            f"  background-color: {tk['bg_default']};"
            f"}}"
            f"QScrollArea QLabel {{"
            f"  color: {tk['text_primary']};"
            f"}}"
        )

    @staticmethod
    def showcase_section_title_style() -> str:
        """Return QSS for showcase section title labels."""
        tk = GalleryStyles._tokens()
        if not tk:
            return ""
        return (
            f"font-size: {tk['font_large']}px;"
            f"font-weight: bold;"
            f"color: {tk['text_primary']};"
            f"margin-top: {tk['spacing_large']}px;"
        )

    @staticmethod
    def showcase_section_desc_style() -> str:
        """Return QSS for showcase section description labels."""
        tk = GalleryStyles._tokens()
        if not tk:
            return ""
        return (
            f"color: {tk['text_secondary']};"
            f"font-size: {tk['font_small']}px;"
            f"margin-bottom: {tk['spacing_small']}px;"
        )
