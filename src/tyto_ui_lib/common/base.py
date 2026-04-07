"""Base widget for all Tyto UI components.

Provides unified lifecycle management, automatic theme subscription,
and a cleanup hook for resource release.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from tyto_ui_lib.core.theme_engine import ThemeEngine


class BaseWidget(QWidget):
    """Abstract base class for all Tyto UI components.

    Automatically connects to the ThemeEngine's ``theme_changed`` signal
    so that subclasses receive style updates whenever the active theme
    changes.  Subclasses should override ``apply_theme`` to fetch tokens
    and update their appearance.

    Args:
        parent: Optional parent widget.

    Example:
        >>> class MyWidget(BaseWidget):
        ...     def apply_theme(self) -> None:
        ...         engine = ThemeEngine.instance()
        ...         bg = engine.get_token("colors", "bg_default")
        ...         self.setStyleSheet(f"background: {bg};")
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        engine = ThemeEngine.instance()
        engine.theme_changed.connect(self._on_theme_changed)

        # Apply current theme if one is already active
        if engine.current_theme():
            self.apply_theme()

    def apply_theme(self) -> None:
        """Fetch current tokens from ThemeEngine and update styles.

        Subclasses should override this method to apply component-specific
        styling based on the active design tokens.  The default
        implementation is intentionally a no-op.
        """

    def _on_theme_changed(self, _theme_name: str) -> None:
        """Slot invoked when the active theme changes.

        Delegates to ``apply_theme`` so subclasses only need to implement
        one method for both initial styling and runtime updates.

        Args:
            _theme_name: Name of the newly activated theme (unused here).
        """
        self.apply_theme()

    def cleanup(self) -> None:
        """Disconnect signals and release resources before destruction.

        Call this method (or ensure it is called) before the widget is
        garbage-collected to avoid dangling signal connections.
        """
        import warnings

        try:
            engine = ThemeEngine.instance()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                engine.theme_changed.disconnect(self._on_theme_changed)
        except (RuntimeError, TypeError):
            # Already disconnected or engine destroyed – safe to ignore.
            pass
