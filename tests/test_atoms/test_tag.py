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


from hypothesis import given, settings
from hypothesis import strategies as st


class TestTTagQSSPropertySelector:
    """Property 36: Tag QSS attribute selector takes effect after creation.

    **Validates: Requirements 22.1, 22.2, 22.3, 22.4**
    """

    # Feature: tyto-ui-lib-v1, Property 36: Tag QSS 属性选择器生效
    @settings(max_examples=100)
    @given(tag_type=st.sampled_from(list(TTag.TagType)))
    def test_tag_type_qss_property(self, qapp: QApplication, tag_type: TTag.TagType) -> None:
        """For any TagType, the created TTag's dynamic property 'tagType' equals the type's value."""
        tag = TTag("Test", tag_type=tag_type)
        assert tag.property("tagType") == tag_type.value


class TestTTagCloseButtonHidesTag:
    """Property 37: Tag close button hides the tag.

    **Validates: Requirements 22.5**
    """

    # Feature: tyto-ui-lib-v1, Property 37: Tag 关闭按钮隐藏标签
    @settings(max_examples=100, deadline=None)
    @given(tag_type=st.sampled_from(list(TTag.TagType)))
    def test_close_button_hides_tag(self, qapp: QApplication, tag_type: TTag.TagType) -> None:
        """For any closable TTag, clicking the close button emits closed and hides the tag."""
        tag = TTag("Test", tag_type=tag_type, closable=True)
        tag.show()
        assert tag.isVisible()

        received: list[bool] = []
        tag.closed.connect(lambda: received.append(True))

        assert tag._close_btn is not None
        tag._close_btn.click()

        assert len(received) == 1
        assert not tag.isVisible()
