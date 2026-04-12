"""Unit tests for the EventBus singleton."""

from __future__ import annotations

import logging

import pytest

from tyto_ui_lib.core.event_bus import EventBus


@pytest.fixture(autouse=True)
def _reset_bus() -> None:
    """Ensure a fresh EventBus for every test."""
    EventBus.reset()


class TestSingleton:
    """EventBus.instance() returns the same object."""

    def test_instance_returns_same_object(self) -> None:
        assert EventBus.instance() is EventBus.instance()

    def test_reset_creates_new_instance(self) -> None:
        first = EventBus.instance()
        EventBus.reset()
        second = EventBus.instance()
        assert first is not second


class TestOnAndEmit:
    """Basic subscribe / publish behaviour."""

    def test_callback_receives_args(self) -> None:
        bus = EventBus.instance()
        received: list[tuple[object, ...]] = []
        bus.on("evt", lambda *a: received.append(a))
        bus.emit("evt", 1, "two")
        assert received == [(1, "two")]

    def test_callback_receives_kwargs(self) -> None:
        bus = EventBus.instance()
        received: list[dict[str, object]] = []
        bus.on("evt", lambda **kw: received.append(kw))
        bus.emit("evt", key="value")
        assert received == [{"key": "value"}]

    def test_subscription_order_preserved(self) -> None:
        bus = EventBus.instance()
        order: list[int] = []
        bus.on("evt", lambda: order.append(1))
        bus.on("evt", lambda: order.append(2))
        bus.on("evt", lambda: order.append(3))
        bus.emit("evt")
        assert order == [1, 2, 3]

    def test_emit_unknown_event_is_noop(self) -> None:
        bus = EventBus.instance()
        bus.emit("nonexistent")  # should not raise


class TestOff:
    """Unsubscribe behaviour."""

    def test_off_removes_callback(self) -> None:
        bus = EventBus.instance()
        calls: list[int] = []
        cb = lambda: calls.append(1)  # noqa: E731
        bus.on("evt", cb)
        bus.off("evt", cb)
        bus.emit("evt")
        assert calls == []

    def test_off_unknown_event_is_noop(self) -> None:
        bus = EventBus.instance()
        bus.off("nonexistent", lambda: None)  # should not raise

    def test_off_unknown_callback_is_noop(self) -> None:
        bus = EventBus.instance()
        bus.on("evt", lambda: None)
        bus.off("evt", lambda: None)  # different lambda — noop


class TestOnce:
    """Single-fire subscription."""

    def test_once_fires_exactly_once(self) -> None:
        bus = EventBus.instance()
        calls: list[int] = []
        bus.once("evt", lambda: calls.append(1))
        bus.emit("evt")
        bus.emit("evt")
        assert calls == [1]

    def test_once_can_be_removed_before_firing(self) -> None:
        bus = EventBus.instance()
        calls: list[int] = []
        cb = lambda: calls.append(1)  # noqa: E731
        bus.once("evt", cb)
        bus.off("evt", cb)
        bus.emit("evt")
        assert calls == []


class TestExceptionIsolation:
    """A failing callback must not prevent others from running."""

    def test_exception_does_not_block_subsequent_callbacks(self, caplog: pytest.LogCaptureFixture) -> None:
        bus = EventBus.instance()
        results: list[str] = []

        def bad_callback() -> None:
            raise ValueError("boom")

        bus.on("evt", lambda: results.append("first"))
        bus.on("evt", bad_callback)
        bus.on("evt", lambda: results.append("third"))

        with caplog.at_level(logging.ERROR):
            bus.emit("evt")

        assert results == ["first", "third"]
        assert "boom" in caplog.text or "Exception in EventBus" in caplog.text


class TestClear:
    """clear() and clear_all() behaviour."""

    def test_clear_removes_all_listeners_for_event(self) -> None:
        bus = EventBus.instance()
        calls: list[int] = []
        bus.on("evt", lambda: calls.append(1))
        bus.on("evt", lambda: calls.append(2))
        bus.clear("evt")
        bus.emit("evt")
        assert calls == []

    def test_clear_does_not_affect_other_events(self) -> None:
        bus = EventBus.instance()
        calls: list[str] = []
        bus.on("a", lambda: calls.append("a"))
        bus.on("b", lambda: calls.append("b"))
        bus.clear("a")
        bus.emit("a")
        bus.emit("b")
        assert calls == ["b"]

    def test_clear_all_removes_everything(self) -> None:
        bus = EventBus.instance()
        calls: list[str] = []
        bus.on("a", lambda: calls.append("a"))
        bus.on("b", lambda: calls.append("b"))
        bus.clear_all()
        bus.emit("a")
        bus.emit("b")
        assert calls == []
