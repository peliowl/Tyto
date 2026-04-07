"""Unit tests for TTag atom component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.tag import TTag
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTTagCreation:
    """Tests for TTag initialization and property assignment."""

    def test_default_properties(self, qapp: QApplication) -> None:
        tag = TTag("hello")
        assert tag.text == "hello"
        assert tag.tag_type == TTag.TagType.DEFAULT
        assert tag.size == TTag.TagSize.MEDIUM
        assert tag.closable is False

    def test_primary_type(self, qapp: QApplication) -> None:
        tag = TTag("ok", tag_type=TTag.TagType.PRIMARY)
        assert tag.tag_type == TTag.TagType.PRIMARY
        assert tag.property("tagType") == "primary"

    def test_all_types(self, qapp: QApplication) -> None:
        for tt in TTag.TagType:
            tag = TTag("t", tag_type=tt)
            assert tag.tag_type == tt

    def test_all_sizes(self, qapp: QApplication) -> None:
        for sz in TTag.TagSize:
            tag = TTag("t", size=sz)
            assert tag.size == sz
            assert tag.property("tagSize") == sz.value

    def test_closable_shows_button(self, qapp: QApplication) -> None:
        tag = TTag("x", closable=True)
        assert tag._close_btn is not None
        assert not tag._close_btn.isHidden()

    def test_not_closable_no_button(self, qapp: QApplication) -> None:
        tag = TTag("x", closable=False)
        assert tag._close_btn is None


class TestTTagClosedSignal:
    """Tests for closed signal emission."""

    def test_close_button_emits_signal(self, qapp: QApplication) -> None:
        tag = TTag("rm", closable=True)
        received: list[bool] = []
        tag.closed.connect(lambda: received.append(True))
        assert tag._close_btn is not None
        tag._close_btn.click()
        assert len(received) == 1

    def test_set_text_updates_label(self, qapp: QApplication) -> None:
        tag = TTag("old")
        tag.set_text("new")
        assert tag.text == "new"
