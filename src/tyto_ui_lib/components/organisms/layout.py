"""TLayout organism component: standard layout container system.

Provides Header/Sider/Content/Footer sub-components for building classic
page layouts.  TLayoutSider supports collapsible width with 200ms animation
and responsive breakpoint-based auto-collapse.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.core.theme_engine import ThemeEngine


def _get_layout_token(key: str, default: Any = None) -> Any:
    """Retrieve a layout token value from the current theme.

    Args:
        key: Token key within the 'layout' category.
        default: Fallback value if token is unavailable.

    Returns:
        The token value, or *default* if unavailable.
    """
    try:
        engine = ThemeEngine.instance()
        tokens = engine.current_tokens()
        if tokens and tokens.layout:
            return tokens.layout.get(key, default)
    except Exception:
        pass
    return default


class Breakpoint(str, Enum):
    """Responsive breakpoint thresholds for TLayoutSider auto-collapse.

    Each value maps to a pixel width below which the sider collapses.
    """

    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


_DEFAULT_BREAKPOINTS: dict[str, int] = {
    "sm": 640,
    "md": 768,
    "lg": 1024,
    "xl": 1280,
}


class TLayoutHeader(BaseWidget):
    """Layout header component with configurable height.

    Renders as a full-width horizontal bar at the top of a TLayout.
    Height is driven by the ``layout.header_height`` design token by
    default and can be overridden via the *height* parameter.

    Args:
        height: Fixed height in pixels.  ``None`` uses the token default.
        parent: Optional parent widget.

    Example:
        >>> header = TLayoutHeader(height=48)
        >>> header.setLayout(QHBoxLayout())
    """

    def __init__(
        self,
        height: int | None = None,
        parent: QWidget | None = None,
    ) -> None:
        # Must set _custom_height BEFORE super().__init__ because
        # BaseWidget.__init__ calls apply_theme() -> _apply_height()
        self._custom_height = height
        super().__init__(parent)
        self._apply_height()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Internal layout for user content
        self._content_layout = QHBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

    # -- Public API --

    @property
    def height(self) -> int:
        """Return the current header height in pixels."""
        return self.maximumHeight()

    def set_height(self, height: int) -> None:
        """Set the header height.

        Args:
            height: Height in pixels.
        """
        self._custom_height = height
        self._apply_height()

    def set_content(self, widget: QWidget) -> None:
        """Set the header content widget.

        Args:
            widget: Widget to display inside the header.
        """
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._content_layout.addWidget(widget)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this header."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("layout.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass
        if hasattr(self, "_custom_height"):
            self._apply_height()

    # -- Private --

    def _apply_height(self) -> None:
        """Set the fixed height from custom value or token default."""
        h = self._custom_height
        if h is None:
            h = int(_get_layout_token("header_height", 64))
        self.setFixedHeight(h)


class TLayoutFooter(BaseWidget):
    """Layout footer component with configurable height.

    Renders as a full-width horizontal bar at the bottom of a TLayout.
    Height is driven by the ``layout.footer_height`` design token by
    default and can be overridden via the *height* parameter.

    Args:
        height: Fixed height in pixels.  ``None`` uses the token default.
        parent: Optional parent widget.

    Example:
        >>> footer = TLayoutFooter(height=48)
    """

    def __init__(
        self,
        height: int | None = None,
        parent: QWidget | None = None,
    ) -> None:
        self._custom_height = height
        super().__init__(parent)
        self._apply_height()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Internal layout for user content
        self._content_layout = QHBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

    # -- Public API --

    @property
    def height(self) -> int:
        """Return the current footer height in pixels."""
        return self.maximumHeight()

    def set_height(self, height: int) -> None:
        """Set the footer height.

        Args:
            height: Height in pixels.
        """
        self._custom_height = height
        self._apply_height()

    def set_content(self, widget: QWidget) -> None:
        """Set the footer content widget.

        Args:
            widget: Widget to display inside the footer.
        """
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._content_layout.addWidget(widget)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this footer."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("layout.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass
        if hasattr(self, "_custom_height"):
            self._apply_height()

    # -- Private --

    def _apply_height(self) -> None:
        """Set the fixed height from custom value or token default."""
        h = self._custom_height
        if h is None:
            h = int(_get_layout_token("footer_height", 64))
        self.setFixedHeight(h)


class TLayoutContent(BaseWidget):
    """Layout content area that fills remaining space.

    Expands to occupy all available space not taken by header, footer,
    or sider components within a TLayout.

    Args:
        parent: Optional parent widget.

    Example:
        >>> content = TLayoutContent()
        >>> content.set_content(my_widget)
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._content_layout = QVBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

    def set_content(self, widget: QWidget) -> None:
        """Set the main content widget.

        Args:
            widget: Widget to display in the content area.
        """
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._content_layout.addWidget(widget)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this content area."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("layout.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass


class TLayoutSider(BaseWidget):
    """Layout sidebar with collapsible width and responsive breakpoints.

    Supports animated collapse/expand (200ms ease-in-out) and automatic
    collapse when the parent window width drops below a configured
    breakpoint threshold.

    Args:
        width: Expanded width in pixels.  ``None`` uses the token default (240).
        collapsed_width: Collapsed width in pixels.  ``None`` uses the token default (48).
        collapsed: Initial collapsed state.
        breakpoint: Responsive breakpoint for auto-collapse (``None`` disables).
        placement: Side placement — ``"left"`` (default) or ``"right"``.
        parent: Optional parent widget.

    Signals:
        collapsed_changed: Emitted with the new collapsed boolean state.

    Example:
        >>> sider = TLayoutSider(width=200, breakpoint=Breakpoint.MD)
        >>> sider.collapsed_changed.connect(lambda c: print("collapsed:", c))
    """

    collapsed_changed = Signal(bool)

    _ANIMATION_DURATION = 200  # ms

    def __init__(
        self,
        width: int | None = None,
        collapsed_width: int | None = None,
        collapsed: bool = False,
        breakpoint: Breakpoint | None = None,
        placement: str = "left",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._custom_width = width
        self._custom_collapsed_width = collapsed_width
        self._collapsed = collapsed
        self._breakpoint = breakpoint
        self._placement = placement
        self._anim: QPropertyAnimation | None = None
        self._anim_max: QPropertyAnimation | None = None

        self.setProperty("placement", placement)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Internal layout for user content
        self._content_layout = QVBoxLayout(self)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)

        # Apply initial width
        self._apply_width(animate=False)

    # -- Public API --

    @property
    def collapsed(self) -> bool:
        """Return whether the sider is currently collapsed."""
        return self._collapsed

    @property
    def expanded_width(self) -> int:
        """Return the expanded width in pixels."""
        w = self._custom_width
        if w is None:
            w = int(_get_layout_token("sider_width", 240))
        return w

    @property
    def collapsed_width_value(self) -> int:
        """Return the collapsed width in pixels."""
        w = self._custom_collapsed_width
        if w is None:
            w = int(_get_layout_token("sider_collapsed_width", 48))
        return w

    @property
    def breakpoint_value(self) -> Breakpoint | None:
        """Return the current responsive breakpoint, or ``None``."""
        return self._breakpoint

    def set_collapsed(self, collapsed: bool, animate: bool = True) -> None:
        """Set the collapsed state.

        Args:
            collapsed: ``True`` to collapse, ``False`` to expand.
            animate: Whether to animate the width transition.
        """
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        self._apply_width(animate=animate)
        self.collapsed_changed.emit(self._collapsed)

    def toggle_collapsed(self) -> None:
        """Toggle between collapsed and expanded states with animation."""
        self.set_collapsed(not self._collapsed)

    def set_width(self, width: int) -> None:
        """Set the expanded width.

        Args:
            width: Width in pixels.
        """
        self._custom_width = width
        if not self._collapsed:
            self._apply_width(animate=False)

    def set_collapsed_width(self, width: int) -> None:
        """Set the collapsed width.

        Args:
            width: Width in pixels.
        """
        self._custom_collapsed_width = width
        if self._collapsed:
            self._apply_width(animate=False)

    def set_breakpoint(self, bp: Breakpoint | None) -> None:
        """Set the responsive breakpoint for auto-collapse.

        Args:
            bp: Breakpoint enum value, or ``None`` to disable.
        """
        self._breakpoint = bp

    def set_content(self, widget: QWidget) -> None:
        """Set the sider content widget.

        Args:
            widget: Widget to display inside the sider.
        """
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self._content_layout.addWidget(widget)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this sider."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("layout.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    # -- Breakpoint handling --

    def check_breakpoint(self, window_width: int) -> None:
        """Evaluate the breakpoint rule against the given window width.

        If a breakpoint is configured and the window width crosses the
        threshold, the sider will auto-collapse or auto-expand.

        Args:
            window_width: Current width of the parent window in pixels.
        """
        if self._breakpoint is None:
            return

        bp_tokens = _get_layout_token("breakpoints", _DEFAULT_BREAKPOINTS)
        threshold = bp_tokens.get(self._breakpoint.value, 768) if isinstance(bp_tokens, dict) else 768

        should_collapse = window_width < threshold
        if should_collapse != self._collapsed:
            self.set_collapsed(should_collapse)

    # -- Private --

    def _apply_width(self, animate: bool = True) -> None:
        """Apply the current width (collapsed or expanded).

        Args:
            animate: Whether to use a 200ms width transition animation.
        """
        target = self.collapsed_width_value if self._collapsed else self.expanded_width

        if not animate or not self.isVisible():
            self.setFixedWidth(target)
            self.setMinimumWidth(target)
            self.setMaximumWidth(target)
            return

        # Stop any running animation
        if self._anim is not None:
            self._anim.stop()
        if self._anim_max is not None:
            self._anim_max.stop()

        self._anim = QPropertyAnimation(self, b"minimumWidth", self)
        self._anim.setDuration(self._ANIMATION_DURATION)
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(target)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Also animate maximumWidth in sync
        self._anim_max = QPropertyAnimation(self, b"maximumWidth", self)
        self._anim_max.setDuration(self._ANIMATION_DURATION)
        self._anim_max.setStartValue(self.width())
        self._anim_max.setEndValue(target)
        self._anim_max.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._anim.start()
        self._anim_max.start()


class TLayout(BaseWidget):
    """Standard layout container implementing Header/Sider/Content/Footer.

    Automatically detects child component types and arranges them using
    nested QHBoxLayout and QVBoxLayout.  When a TLayoutSider is present,
    it is placed beside the vertical column containing header, content,
    and footer.

    Supports classic layout combinations:
    - Header + Content + Footer
    - Header + Sider + Content + Footer
    - Sider + Content
    - Sider + Header + Content + Footer

    The layout forwards ``resizeEvent`` to any TLayoutSider children so
    that responsive breakpoint rules can be evaluated.

    Args:
        parent: Optional parent widget.

    Example:
        >>> layout = TLayout()
        >>> layout.add_header(TLayoutHeader())
        >>> layout.add_sider(TLayoutSider(width=200))
        >>> layout.add_content(TLayoutContent())
        >>> layout.add_footer(TLayoutFooter())
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._header: TLayoutHeader | None = None
        self._footer: TLayoutFooter | None = None
        self._sider: TLayoutSider | None = None
        self._content: TLayoutContent | None = None

        # Root layout — will be rebuilt when children are added
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

    # -- Public API --

    def add_header(self, header: TLayoutHeader) -> None:
        """Add a header component to the layout.

        Args:
            header: The header widget.
        """
        self._header = header
        self._rebuild_layout()

    def add_footer(self, footer: TLayoutFooter) -> None:
        """Add a footer component to the layout.

        Args:
            footer: The footer widget.
        """
        self._footer = footer
        self._rebuild_layout()

    def add_sider(self, sider: TLayoutSider) -> None:
        """Add a sidebar component to the layout.

        Args:
            sider: The sidebar widget.
        """
        self._sider = sider
        self._rebuild_layout()

    def add_content(self, content: TLayoutContent) -> None:
        """Add the main content component to the layout.

        Args:
            content: The content widget.
        """
        self._content = content
        self._rebuild_layout()

    @property
    def header(self) -> TLayoutHeader | None:
        """Return the header widget, or ``None``."""
        return self._header

    @property
    def footer(self) -> TLayoutFooter | None:
        """Return the footer widget, or ``None``."""
        return self._footer

    @property
    def sider(self) -> TLayoutSider | None:
        """Return the sider widget, or ``None``."""
        return self._sider

    @property
    def content(self) -> TLayoutContent | None:
        """Return the content widget, or ``None``."""
        return self._content

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme QSS to this layout container."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("layout.qss.j2")
            self.setStyleSheet(qss)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass

    # -- Events --

    def resizeEvent(self, event: Any) -> None:
        """Forward resize events to sider for breakpoint evaluation."""
        super().resizeEvent(event)
        if self._sider is not None:
            self._sider.check_breakpoint(self.width())

    # -- Private --

    def _rebuild_layout(self) -> None:
        """Rebuild the internal layout hierarchy from current children.

        Layout strategy:
        - If a sider exists, use an HBoxLayout with the sider on one side
          and a vertical column (header + content + footer) on the other.
        - If no sider, use a simple VBoxLayout with header + content + footer.
        """
        # Remove all items from root layout without deleting widgets
        while self._root_layout.count():
            item = self._root_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
            inner = item.layout()
            if inner is not None:
                self._clear_layout(inner)

        if self._sider is not None:
            # Horizontal: sider | vertical(header, content, footer)
            h_container = QWidget(self)
            h_layout = QHBoxLayout(h_container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(0)

            v_container = QWidget(h_container)
            v_layout = QVBoxLayout(v_container)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(0)

            if self._header is not None:
                self._header.setParent(v_container)
                v_layout.addWidget(self._header)

            if self._content is not None:
                self._content.setParent(v_container)
                v_layout.addWidget(self._content, 1)

            if self._footer is not None:
                self._footer.setParent(v_container)
                v_layout.addWidget(self._footer)

            # Place sider on left or right based on placement
            if self._sider._placement == "right":
                v_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                h_layout.addWidget(v_container, 1)
                self._sider.setParent(h_container)
                h_layout.addWidget(self._sider)
            else:
                self._sider.setParent(h_container)
                h_layout.addWidget(self._sider)
                v_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                h_layout.addWidget(v_container, 1)

            self._root_layout.addWidget(h_container)
        else:
            # Simple vertical: header, content, footer
            if self._header is not None:
                self._header.setParent(self)
                self._root_layout.addWidget(self._header)

            if self._content is not None:
                self._content.setParent(self)
                self._root_layout.addWidget(self._content, 1)

            if self._footer is not None:
                self._footer.setParent(self)
                self._root_layout.addWidget(self._footer)

    @staticmethod
    def _clear_layout(layout: QVBoxLayout | QHBoxLayout) -> None:  # type: ignore[override]
        """Recursively remove all items from a layout without deleting widgets."""
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
            inner = item.layout()
            if inner is not None:
                TLayout._clear_layout(inner)
