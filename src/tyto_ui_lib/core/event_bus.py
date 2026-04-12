"""Global event bus for publish/subscribe communication between components.

Provides a singleton EventBus that enables decoupled communication between
non-parent-child components, reducing the complexity of cross-hierarchy
signal-slot connections.

Example:
    >>> bus = EventBus.instance()
    >>> bus.on("user:login", lambda name: print(f"Welcome, {name}"))
    >>> bus.emit("user:login", "Alice")
    Welcome, Alice
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class _OnceWrapper:
    """Internal wrapper that auto-unsubscribes after a single invocation."""

    __slots__ = ("_bus", "_event", "_callback")

    def __init__(self, bus: EventBus, event: str, callback: Any) -> None:
        self._bus = bus
        self._event = event
        self._callback = callback

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._bus.off(self._event, self)
        return self._callback(*args, **kwargs)

    @property
    def original(self) -> Any:
        """Return the original callback for identity comparison."""
        return self._callback


class EventBus:
    """Singleton global event bus for publish/subscribe messaging.

    The EventBus allows any component to emit named events and any other
    component to subscribe to those events, without requiring a direct
    parent-child relationship or Qt signal-slot wiring.

    Callbacks are invoked in subscription order. If a callback raises an
    exception, the error is logged and remaining callbacks still execute.

    Example:
        >>> bus = EventBus.instance()
        >>> results = []
        >>> bus.on("ping", lambda: results.append("pong"))
        >>> bus.emit("ping")
        >>> results
        ['pong']
    """

    _instance: ClassVar[EventBus | None] = None

    def __init__(self) -> None:
        self._listeners: defaultdict[str, list[Any]] = defaultdict(list)

    @classmethod
    def instance(cls) -> EventBus:
        """Return the singleton EventBus instance, creating it if needed.

        Returns:
            The global EventBus singleton.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Primarily for testing."""
        if cls._instance is not None:
            cls._instance.clear_all()
        cls._instance = None

    def on(self, event_name: str, callback: Any) -> None:
        """Subscribe *callback* to *event_name*.

        Callbacks are called in the order they were registered.

        Args:
            event_name: The event identifier string.
            callback: A callable to invoke when the event is emitted.
        """
        self._listeners[event_name].append(callback)

    def off(self, event_name: str, callback: Any) -> None:
        """Unsubscribe *callback* from *event_name*.

        If the callback was registered via :meth:`once`, it can be removed
        by passing the original callback reference.

        Args:
            event_name: The event identifier string.
            callback: The callable to remove.
        """
        listeners = self._listeners.get(event_name)
        if listeners is None:
            return

        for i, listener in enumerate(listeners):
            if listener is callback:
                listeners.pop(i)
                return
            if isinstance(listener, _OnceWrapper) and listener.original is callback:
                listeners.pop(i)
                return

    def once(self, event_name: str, callback: Any) -> None:
        """Subscribe *callback* to *event_name* for a single invocation.

        The callback is automatically unsubscribed after it fires once.

        Args:
            event_name: The event identifier string.
            callback: A callable to invoke once when the event is emitted.
        """
        wrapper = _OnceWrapper(self, event_name, callback)
        self._listeners[event_name].append(wrapper)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Publish an event, invoking all subscribed callbacks in order.

        If a callback raises an exception, the error is logged and
        execution continues with the remaining callbacks.

        Args:
            event_name: The event identifier string.
            *args: Positional arguments forwarded to each callback.
            **kwargs: Keyword arguments forwarded to each callback.
        """
        listeners = list(self._listeners.get(event_name, []))
        for listener in listeners:
            try:
                listener(*args, **kwargs)
            except Exception:
                logger.exception(
                    "Exception in EventBus callback for event '%s'",
                    event_name,
                )

    def clear(self, event_name: str) -> None:
        """Remove all subscriptions for *event_name*.

        Args:
            event_name: The event identifier string.
        """
        self._listeners.pop(event_name, None)

    def clear_all(self) -> None:
        """Remove all subscriptions for all events."""
        self._listeners.clear()
