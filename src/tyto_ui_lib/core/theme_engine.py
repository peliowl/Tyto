"""Theme engine singleton for managing design tokens and QSS rendering.

The ThemeEngine loads design tokens from JSON files, renders Jinja2 QSS
templates with token values, and emits signals on theme changes so that
all widgets can update their styles automatically.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import Any, ClassVar

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.core.tokens import DesignTokenSet, load_tokens_from_file


def _default_tokens_dir() -> Path:
    """Return the path to the built-in styles/tokens directory."""
    pkg = importlib.resources.files("tyto_ui_lib") / "styles" / "tokens"
    return Path(str(pkg))


def _default_templates_dir() -> Path:
    """Return the path to the built-in styles/templates directory."""
    pkg = importlib.resources.files("tyto_ui_lib") / "styles" / "templates"
    return Path(str(pkg))


class ThemeEngine(QObject):
    """Singleton theme engine that manages design tokens and renders QSS.

    The ThemeEngine loads token definitions from JSON files, maintains the
    current theme state, renders Jinja2 QSS templates with token values,
    and notifies all connected widgets when the theme changes.

    Signals:
        theme_changed: Emitted after a theme switch with the new theme name.

    Example:
        >>> engine = ThemeEngine.instance()
        >>> engine.load_tokens("path/to/tokens/")
        >>> engine.switch_theme("dark")
        >>> engine.get_token("colors", "primary")
        '#63e2b7'
    """

    theme_changed = Signal(str)

    _instance: ClassVar[ThemeEngine | None] = None

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._themes: dict[str, DesignTokenSet] = {}
        self._current_theme: str = ""
        self._jinja_env: Environment | None = None

    @classmethod
    def instance(cls) -> ThemeEngine:
        """Return the singleton ThemeEngine instance, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Primarily for testing."""
        cls._instance = None

    def load_tokens(self, tokens_dir: str | Path | None = None) -> None:
        """Load all theme token files from a directory.

        Scans the directory for JSON files and loads each as a theme.
        Also initialises the Jinja2 template environment.

        Args:
            tokens_dir: Path to directory containing token JSON files.
                Falls back to the built-in styles/tokens/ directory.

        Raises:
            FileNotFoundError: If the directory does not exist.
            TokenFileError: If any token file is invalid.
        """
        if tokens_dir is None:
            tokens_dir = _default_tokens_dir()
        tokens_path = Path(tokens_dir)

        if not tokens_path.is_dir():
            raise FileNotFoundError(f"Tokens directory not found: {tokens_path}")

        for json_file in sorted(tokens_path.glob("*.json")):
            token_set = load_tokens_from_file(json_file)
            theme_name = token_set.name or json_file.stem
            self._themes[theme_name] = token_set

        # Initialise Jinja2 environment from the templates directory
        templates_dir = _default_templates_dir()
        if templates_dir.is_dir():
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                undefined=StrictUndefined,
                autoescape=False,
            )

    def switch_theme(self, theme_name: str) -> None:
        """Switch to the specified theme and re-apply global QSS.

        Args:
            theme_name: Name of the theme to activate (e.g. "light", "dark").

        Raises:
            ValueError: If the theme name is not loaded.
        """
        if theme_name not in self._themes:
            available = ", ".join(sorted(self._themes.keys())) or "(none)"
            raise ValueError(f"Unknown theme '{theme_name}'. Available: {available}")

        self._current_theme = theme_name

        # Re-render and apply global stylesheet
        app = QApplication.instance()
        if app is not None:
            qss = self._render_all_templates()
            app.setStyleSheet(qss)

        self.theme_changed.emit(theme_name)

    def get_token(self, category: str, key: str) -> str | int:
        """Retrieve a single token value from the current theme.

        Args:
            category: Token category (e.g. "colors", "spacing").
            key: Token key within the category (e.g. "primary", "medium").

        Returns:
            The token value (str for colors/shadows, int for spacing/radius/font_sizes).

        Raises:
            RuntimeError: If no theme is active.
            KeyError: If the category or key does not exist.
        """
        if not self._current_theme:
            raise RuntimeError("No active theme. Call switch_theme() first.")

        tokens = self._themes[self._current_theme]
        section: dict[str, Any] = getattr(tokens, category)
        return section[key]

    def current_theme(self) -> str:
        """Return the name of the currently active theme.

        Returns:
            Theme name string, or empty string if no theme is active.
        """
        return self._current_theme

    def current_tokens(self) -> DesignTokenSet | None:
        """Return the DesignTokenSet for the current theme, or None."""
        return self._themes.get(self._current_theme)

    def render_qss(self, template_name: str, **extra_context: Any) -> str:
        """Render a single Jinja2 QSS template with current token values.

        Args:
            template_name: Template filename (e.g. "button.qss.j2").
            **extra_context: Additional variables passed to the template.

        Returns:
            Rendered QSS string.

        Raises:
            RuntimeError: If no theme is active or Jinja2 env is not ready.
        """
        if self._jinja_env is None:
            raise RuntimeError("Jinja2 environment not initialised. Call load_tokens() first.")
        if not self._current_theme:
            raise RuntimeError("No active theme. Call switch_theme() first.")

        tokens = self._themes[self._current_theme]
        context: dict[str, Any] = {
            "colors": tokens.colors,
            "spacing": tokens.spacing,
            "radius": tokens.radius,
            "font_sizes": tokens.font_sizes,
            "shadows": tokens.shadows,
            "component_sizes": tokens.component_sizes,
            "switch_sizes": tokens.switch_sizes,
            "spin_sizes": tokens.spin_sizes,
            "slider": tokens.slider,
            "layout": tokens.layout,
            "card": tokens.card,
            "menu": tokens.menu,
            "theme": tokens.name,
            **extra_context,
        }

        template = self._jinja_env.get_template(template_name)
        return template.render(context)

    # -- Private helpers --

    def _render_all_templates(self) -> str:
        """Render all available QSS templates and concatenate them."""
        if self._jinja_env is None:
            return ""

        parts: list[str] = []
        loader = self._jinja_env.loader
        if loader is not None:
            template_names = loader.list_templates()
            for name in sorted(template_names):
                if name.endswith(".qss.j2"):
                    try:
                        parts.append(self.render_qss(name))
                    except Exception:
                        # Skip templates that fail (e.g. missing extra context)
                        pass
        return "\n".join(parts)
