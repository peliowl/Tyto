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


class TestTTagInfoType:
    """Property 61: Tag Info type correctness.

    For any TagType enum value (including the new INFO), creating a TTag
    with that type should set the tag_type property to the passed value.

    **Validates: Requirements 36.1**
    """

    # Feature: tyto-ui-lib-v1, Property 61: Tag Info 类型正确性
    @settings(max_examples=100)
    @given(tag_type=st.sampled_from(list(TTag.TagType)))
    def test_tag_info_type_correctness(self, qapp: QApplication, tag_type: TTag.TagType) -> None:
        """For any TagType (including INFO), tag_type property equals the passed value."""
        tag = TTag("Test", tag_type=tag_type)
        assert tag.tag_type == tag_type
        assert tag.property("tagType") == tag_type.value


class TestTTagTinySize:
    """Property 62: Tag Tiny size correctness.

    For any TagSize enum value (including the new TINY), creating a TTag
    with that size should set the size property to the passed value.

    **Validates: Requirements 36.2**
    """

    # Feature: tyto-ui-lib-v1, Property 62: Tag Tiny 尺寸正确性
    @settings(max_examples=100)
    @given(tag_size=st.sampled_from(list(TTag.TagSize)))
    def test_tag_tiny_size_correctness(self, qapp: QApplication, tag_size: TTag.TagSize) -> None:
        """For any TagSize (including TINY), size property equals the passed value."""
        tag = TTag("Test", size=tag_size)
        assert tag.size == tag_size
        assert tag.property("tagSize") == tag_size.value


class TestTTagCheckableToggle:
    """Property 63: Tag Checkable Toggle Round-Trip.

    For any checkable=True TTag, clicking toggles is_checked() to the opposite
    value, and clicking again returns to the initial value. checked_changed
    signal carries the correct boolean.

    **Validates: Requirements 36.7, 36.8**
    """

    # Feature: tyto-ui-lib-v1, Property 63: Tag Checkable Toggle Round-Trip
    @settings(max_examples=100, deadline=None)
    @given(initial_checked=st.booleans())
    def test_tag_checkable_toggle_roundtrip(self, qapp: QApplication, initial_checked: bool) -> None:
        """Toggling a checkable tag twice returns to the initial checked state."""
        tag = TTag("Filter", checkable=True, checked=initial_checked)
        assert tag.is_checked() == initial_checked

        signals: list[bool] = []
        tag.checked_changed.connect(lambda v: signals.append(v))

        # First toggle
        tag.set_checked(not initial_checked)
        assert tag.is_checked() == (not initial_checked)
        assert len(signals) == 1
        assert signals[0] == (not initial_checked)

        # Second toggle (round-trip)
        tag.set_checked(initial_checked)
        assert tag.is_checked() == initial_checked
        assert len(signals) == 2
        assert signals[1] == initial_checked


class TestTTagCustomColor:
    """Property 64: Tag custom color override.

    For any custom color dict (with color / border_color / text_color),
    setting it on a TTag should apply those colors as inline stylesheet.

    **Validates: Requirements 36.6**
    """

    # Feature: tyto-ui-lib-v1, Property 64: Tag 自定义颜色覆盖
    @settings(max_examples=100, deadline=None)
    @given(
        bg=st.from_regex(r"#[0-9a-f]{6}", fullmatch=True),
        border=st.from_regex(r"#[0-9a-f]{6}", fullmatch=True),
        text=st.from_regex(r"#[0-9a-f]{6}", fullmatch=True),
    )
    def test_tag_custom_color_override(self, qapp: QApplication, bg: str, border: str, text: str) -> None:
        """Custom color dict overrides the tag's inline stylesheet."""
        color_dict = {"color": bg, "border_color": border, "text_color": text}
        tag = TTag("Custom", color=color_dict)

        ss = tag.styleSheet()
        assert bg in ss
        assert border in ss
        assert text in ss
