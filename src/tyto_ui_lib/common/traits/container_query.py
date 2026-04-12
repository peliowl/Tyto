"""Container query mixin: responsive breakpoint system based on parent container size.

Uses ``QResizeEvent`` via an event filter installed on the parent widget to
detect size changes.  No polling is used.  Components mixing in this class
can register named breakpoints and receive callbacks when the parent
container crosses breakpoint boundaries.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class _Breakpoint:
    """Internal breakpoint definition."""

    name: str
    min_width: int
    max_width: int


class _ResizeFilter(QObject):
    """Event filter that forwards parent resize events to the mixin owner."""

    def __init__(self, owner: ContainerQueryMixin, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._owner = owner

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Intercept resize events and delegate to the mixin owner.

        Args:
            obj: The watched object (parent widget).
            event: The event to filter.

        Returns:
            False so the event continues to propagate.
        """
        if event.type() == QEvent.Type.Resize:
            widget = obj
            if isinstance(widget, QWidget):
                size = widget.size()
                self._owner.container_resized(size.width(), size.height())
        return False


class ContainerQueryMixin:
    """Mixin enabling container query responsive behavior.

    Components mixing in this class can register breakpoints and
    receive callbacks when their parent container crosses breakpoint
    boundaries.  Uses ``QResizeEvent``, no polling.

    Designed for cooperative multiple inheritance with ``BaseWidget``
    (or any ``QWidget`` subclass).

    Example:
        >>> class MyWidget(ContainerQueryMixin, BaseWidget):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.add_breakpoint("compact", 0, 400)
        ...         self.add_breakpoint("normal", 401, 800)
        ...         self.breakpoint_changed.connect(self._on_bp)
    """

    breakpoint_changed = Signal(str)

    _cq_breakpoints: list[_Breakpoint]
    _cq_current: str | None
    _cq_resize_filter: _ResizeFilter | None

    def _init_container_query(self) -> None:
        """Initialise container query resources.  Call from ``__init__``."""
        self._cq_breakpoints = []
        self._cq_current = None
        self._cq_resize_filter = None

    def add_breakpoint(self, name: str, min_width: int, max_width: int) -> None:
        """Register a named breakpoint rule.

        Args:
            name: Human-readable breakpoint name (e.g. ``"compact"``).
            min_width: Minimum container width (inclusive) for this breakpoint.
            max_width: Maximum container width (inclusive) for this breakpoint.
        """
        self._cq_breakpoints.append(_Breakpoint(name=name, min_width=min_width, max_width=max_width))

    def current_breakpoint(self) -> str | None:
        """Return the name of the currently matched breakpoint.

        Returns:
            The breakpoint name, or ``None`` if no breakpoint matches.
        """
        return self._cq_current

    def container_resized(self, width: int, height: int) -> None:
        """Called when the parent container size changes.

        Evaluates registered breakpoints against the new *width* and emits
        ``breakpoint_changed`` if the matched breakpoint has changed.
        Subclasses may override this for custom resize logic but should
        call ``super().container_resized(width, height)`` to preserve
        breakpoint evaluation.

        Args:
            width: New container width in pixels.
            height: New container height in pixels.
        """
        matched: str | None = None
        for bp in self._cq_breakpoints:
            if bp.min_width <= width <= bp.max_width:
                matched = bp.name
                break

        if matched != self._cq_current:
            self._cq_current = matched
            if matched is not None:
                self.breakpoint_changed.emit(matched)  # type: ignore[attr-defined]

    def _install_resize_filter(self) -> None:
        """Install an event filter on the parent widget to capture ``QResizeEvent``.

        If the parent widget is ``None``, a warning is logged and no filter
        is installed.  Call this method after the widget has been added to
        a parent (e.g. at the end of ``__init__`` or in ``showEvent``).
        """
        widget: QWidget = self  # type: ignore[assignment]
        parent = widget.parentWidget()

        if parent is None:
            logger.warning(
                "ContainerQueryMixin: parent is None for %s; "
                "resize filter not installed. Call _install_resize_filter() "
                "again after reparenting.",
                type(self).__name__,
            )
            return

        # Remove previous filter if any
        if self._cq_resize_filter is not None:
            old_parent = self._cq_resize_filter.parent()
            if old_parent is not None and isinstance(old_parent, QWidget):
                old_parent.removeEventFilter(self._cq_resize_filter)
            self._cq_resize_filter.deleteLater()

        self._cq_resize_filter = _ResizeFilter(self, parent)
        parent.installEventFilter(self._cq_resize_filter)

        # Evaluate current parent size immediately
        size = parent.size()
        if size.width() > 0 or size.height() > 0:
            self.container_resized(size.width(), size.height())
