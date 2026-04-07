"""TInputGroup molecule component: compact horizontal widget group.

Arranges child widgets (typically TInput and TButton) in a tight
horizontal row and automatically merges border-radius so that only
the first and last children retain their outer corners.
"""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QHBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


class TInputGroup(BaseWidget):
    """Input group component for compact horizontal arrangement.

    Automatically manages border-radius merging: the first child keeps
    its left-side radius, the last child keeps its right-side radius,
    and all middle children have zero radius. This invariant is
    maintained after every add, insert, or remove operation.

    Args:
        parent: Optional parent widget.

    Example:
        >>> group = TInputGroup()
        >>> group.add_widget(TInput(placeholder="URL"))
        >>> group.add_widget(TButton("Go", button_type=TButton.ButtonType.PRIMARY))
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        self._children: list[QWidget] = []

        super().__init__(parent)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    # -- Public API --

    def add_widget(self, widget: QWidget) -> None:
        """Append a widget to the group and recalculate radius.

        Args:
            widget: The widget to add.
        """
        self._children.append(widget)
        self._layout.addWidget(widget)
        self._recalculate_radius()

    def insert_widget(self, index: int, widget: QWidget) -> None:
        """Insert a widget at the given index and recalculate radius.

        Args:
            index: Position to insert at (clamped to valid range).
            widget: The widget to insert.
        """
        index = max(0, min(index, len(self._children)))
        self._children.insert(index, widget)
        self._layout.insertWidget(index, widget)
        self._recalculate_radius()

    def remove_widget(self, widget: QWidget) -> None:
        """Remove a widget from the group and recalculate radius.

        Args:
            widget: The widget to remove.
        """
        if widget in self._children:
            self._children.remove(widget)
            self._layout.removeWidget(widget)
            widget.setParent(None)  # type: ignore[call-overload]
            self._recalculate_radius()

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this input group."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("inputgroup.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass
        self._recalculate_radius()

    # -- Size hint --

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(300, 34)

    # -- Private --

    def _recalculate_radius(self) -> None:
        """Recalculate border-radius for all children.

        First child: left-side radius only.
        Last child: right-side radius only.
        Middle children: zero radius.
        Single child: full radius (no override).
        """
        engine = ThemeEngine.instance()
        try:
            r = engine.get_token("radius", "medium")
        except (RuntimeError, KeyError):
            r = 4  # Fallback only used when no theme is loaded

        n = len(self._children)
        if n == 0:
            return

        if n == 1:
            # Single child keeps full radius
            self._children[0].setProperty("groupPosition", "solo")
            self._children[0].setStyleSheet("")
            return

        for i, child in enumerate(self._children):
            if i == 0:
                child.setProperty("groupPosition", "first")
                child.setStyleSheet(
                    f"* {{ border-top-left-radius: {r}px; border-bottom-left-radius: {r}px;"
                    f" border-top-right-radius: 0px; border-bottom-right-radius: 0px; }}"
                )
            elif i == n - 1:
                child.setProperty("groupPosition", "last")
                child.setStyleSheet(
                    f"* {{ border-top-right-radius: {r}px; border-bottom-right-radius: {r}px;"
                    f" border-top-left-radius: 0px; border-bottom-left-radius: 0px; }}"
                )
            else:
                child.setProperty("groupPosition", "middle")
                child.setStyleSheet(
                    "* { border-radius: 0px; }"
                )
