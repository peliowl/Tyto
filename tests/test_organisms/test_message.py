"""Unit tests for TMessage organism component and MessageManager."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.organisms.message import (
    MessageManager,
    MessageType,
    TMessage,
    _MESSAGE_GAP,
    _TOP_MARGIN,
)
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_singletons() -> None:
    ThemeEngine.reset()
    MessageManager.reset()
    yield  # type: ignore[misc]
    MessageManager.reset()
    ThemeEngine.reset()


class TestTMessageCreation:
    """Tests for TMessage initialization and properties."""

    def test_default_type_is_info(self, qapp: QApplication) -> None:
        msg = TMessage("hello")
        assert msg.msg_type == MessageType.INFO

    def test_all_types(self, qapp: QApplication) -> None:
        for mt in MessageType:
            msg = TMessage("t", msg_type=mt)
            assert msg.msg_type == mt
            assert msg.property("messageType") == mt.value

    def test_text_property(self, qapp: QApplication) -> None:
        msg = TMessage("test text")
        assert msg.text == "test text"

    def test_duration_property(self, qapp: QApplication) -> None:
        msg = TMessage("d", duration=5000)
        assert msg.duration == 5000

    def test_zero_duration_no_auto_dismiss(self, qapp: QApplication) -> None:
        msg = TMessage("d", duration=0)
        assert msg.duration == 0
        assert not msg._timer.isActive()


class TestTMessageClosedSignal:
    """Tests for closed signal emission."""

    def test_close_emits_signal(self, qapp: QApplication) -> None:
        msg = TMessage("bye", duration=0)
        received: list[bool] = []
        msg.closed.connect(lambda: received.append(True))
        # Directly call the finish handler to avoid animation timing
        msg._on_close_finished()
        assert len(received) == 1


class TestMessageManagerCreation:
    """Tests for MessageManager convenience methods."""

    def test_info_creates_info_message(self, qapp: QApplication) -> None:
        msg = MessageManager.info("info msg", duration=0)
        assert msg.msg_type == MessageType.INFO
        assert msg.text == "info msg"

    def test_success_creates_success_message(self, qapp: QApplication) -> None:
        msg = MessageManager.success("ok", duration=0)
        assert msg.msg_type == MessageType.SUCCESS

    def test_warning_creates_warning_message(self, qapp: QApplication) -> None:
        msg = MessageManager.warning("warn", duration=0)
        assert msg.msg_type == MessageType.WARNING

    def test_error_creates_error_message(self, qapp: QApplication) -> None:
        msg = MessageManager.error("err", duration=0)
        assert msg.msg_type == MessageType.ERROR


class TestMessageManagerStacking:
    """Tests for message stacking and position management."""

    def test_single_message_at_top_margin(self, qapp: QApplication) -> None:
        MessageManager.info("one", duration=0)
        slots = MessageManager.active_slots()
        assert len(slots) == 1
        assert slots[0].y_offset == _TOP_MARGIN

    def test_multiple_messages_stack_with_gap(self, qapp: QApplication) -> None:
        MessageManager.info("a", duration=0)
        MessageManager.info("b", duration=0)
        MessageManager.info("c", duration=0)
        slots = MessageManager.active_slots()
        assert len(slots) == 3
        # y_offsets should be strictly increasing
        for i in range(1, len(slots)):
            assert slots[i].y_offset > slots[i - 1].y_offset

    def test_created_at_strictly_increasing(self, qapp: QApplication) -> None:
        import time

        MessageManager.info("x", duration=0)
        time.sleep(0.01)
        MessageManager.info("y", duration=0)
        slots = MessageManager.active_slots()
        assert slots[1].created_at > slots[0].created_at

    def test_reset_clears_slots(self, qapp: QApplication) -> None:
        MessageManager.info("z", duration=0)
        assert len(MessageManager.active_slots()) == 1
        MessageManager.reset()
        assert len(MessageManager.active_slots()) == 0


# ---------------------------------------------------------------------------
# Property-Based Tests for Bug Fixes (V1.0.1)
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QWidget


class TestMessageWindowCentering:
    """Property 38: Message window centred positioning.

    For any TMessage with a parent window, the message's horizontal centre
    should align with the parent window's horizontal centre (within 1px),
    and the message's top should be near the parent window's top.

    **Validates: Requirements 24.1, 24.4**
    """

    # Feature: tyto-ui-lib-v1, Property 38: Message 窗口居中定位
    @settings(max_examples=100, deadline=None)
    @given(
        msg_type=st.sampled_from(list(MessageType)),
        parent_w=st.integers(min_value=300, max_value=1200),
        parent_h=st.integers(min_value=200, max_value=800),
    )
    def test_message_centred_on_parent(
        self,
        qapp: QApplication,
        msg_type: MessageType,
        parent_w: int,
        parent_h: int,
    ) -> None:
        """Message horizontal centre aligns with parent horizontal centre."""
        MessageManager.reset()

        parent = QWidget()
        parent.resize(parent_w, parent_h)

        msg = TMessage("test", msg_type=msg_type, duration=0, parent=parent)
        msg.adjustSize()

        # Manually trigger position calculation via the manager helper
        mgr = MessageManager.instance()
        from tyto_ui_lib.components.organisms.message import MessageSlot

        slot = MessageSlot(message=msg)
        mgr._slots.append(slot)
        mgr._update_positions()

        # The message's horizontal centre should match the parent's horizontal centre
        parent_global = parent.mapToGlobal(QPoint(0, 0))
        expected_cx = parent_global.x() + parent_w // 2
        actual_cx = msg.x() + msg.width() // 2
        assert abs(actual_cx - expected_cx) <= 1, (
            f"Message centre {actual_cx} != parent centre {expected_cx}"
        )

        # The message top should be at parent_global_y + _TOP_MARGIN
        expected_y = parent_global.y() + _TOP_MARGIN
        assert msg.y() == expected_y, f"Message y {msg.y()} != expected {expected_y}"

        mgr._slots.clear()


class TestMessageBackgroundAndBorderVisible:
    """Property 39: Message background colour and border are visible.

    For any MessageType, a created TMessage should NOT have the
    WA_TranslucentBackground attribute set, ensuring QSS background-color
    and border rules render correctly.

    **Validates: Requirements 24.2**
    """

    # Feature: tyto-ui-lib-v1, Property 39: Message 背景色和边框可见
    @settings(max_examples=100)
    @given(msg_type=st.sampled_from(list(MessageType)))
    def test_message_not_translucent(
        self,
        qapp: QApplication,
        msg_type: MessageType,
    ) -> None:
        """TMessage should not have WA_TranslucentBackground set."""
        msg = TMessage("test", msg_type=msg_type, duration=0)
        assert not msg.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground), (
            f"TMessage with type {msg_type} should not have WA_TranslucentBackground"
        )
