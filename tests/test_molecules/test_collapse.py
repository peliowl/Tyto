"""Unit tests for TCollapse and TCollapseItem molecule components."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from tyto_ui_lib.components.molecules.collapse import (
    TCollapse,
    TCollapseItem,
    _CollapseArrowWidget,
)
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTCollapseItemCreation:
    """Tests for TCollapseItem initialization and properties."""

    def test_default_state(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="Section 1")
        assert item.item_name == "s1"
        assert item.title == "Section 1"
        assert item.expanded is False
        assert item.disabled is False

    def test_expanded_initial(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1", expanded=True)
        assert item.expanded is True

    def test_disabled_initial(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1", disabled=True)
        assert item.disabled is True
        assert item.property("disabled") == "true"
        assert item._header.cursor().shape() == Qt.CursorShape.ForbiddenCursor

    def test_title_setter(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="Old")
        item.title = "New"
        assert item.title == "New"
        assert item._title_label.text() == "New"

    def test_disabled_setter(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1")
        item.disabled = True
        assert item.disabled is True
        assert item.property("disabled") == "true"
        item.disabled = False
        assert item.disabled is False
        assert item._header.cursor().shape() == Qt.CursorShape.PointingHandCursor


class TestTCollapseItemContent:
    """Tests for set_content method."""

    def test_set_content(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1")
        label = QLabel("Content")
        item.set_content(label)
        assert item._content_widget is label

    def test_set_content_replaces(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1")
        label1 = QLabel("First")
        label2 = QLabel("Second")
        item.set_content(label1)
        item.set_content(label2)
        assert item._content_widget is label2


class TestTCollapseItemExpandCollapse:
    """Tests for expand/collapse behavior."""

    def test_set_expanded_no_animate(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1")
        signals: list[bool] = []
        item.expanded_changed.connect(lambda v: signals.append(v))
        item.set_expanded(True, animate=False)
        assert item.expanded is True
        assert len(signals) == 1
        assert signals[0] is True

    def test_set_expanded_same_state_noop(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1", expanded=True)
        signals: list[bool] = []
        item.expanded_changed.connect(lambda v: signals.append(v))
        item.set_expanded(True, animate=False)
        assert len(signals) == 0

    def test_toggle(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1")
        item.set_expanded(True, animate=False)
        assert item.expanded is True
        item.set_expanded(False, animate=False)
        assert item.expanded is False

    def test_toggle_disabled_noop(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1", disabled=True)
        signals: list[bool] = []
        item.expanded_changed.connect(lambda v: signals.append(v))
        item.toggle()
        assert item.expanded is False
        assert len(signals) == 0

    def test_arrow_updates(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="s1", title="S1")
        assert isinstance(item._arrow_label, _CollapseArrowWidget)
        assert item._arrow_label._expanded is False
        item.set_expanded(True, animate=False)
        assert item._arrow_label._expanded is True
        item.set_expanded(False, animate=False)
        assert item._arrow_label._expanded is False
        # Verify re-expanding updates arrow state correctly
        item.set_expanded(True, animate=False)
        assert item._arrow_label._expanded is True


class TestTCollapse:
    """Tests for TCollapse container."""

    def test_add_item(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        assert len(collapse.items) == 1
        assert collapse.items[0].item_name == "a"

    def test_remove_item(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        collapse.remove_item(item)
        assert len(collapse.items) == 0

    def test_expanded_names_initial(self, qapp: QApplication) -> None:
        collapse = TCollapse(expanded_names=["b"])
        item_a = TCollapseItem(name="a", title="A")
        item_b = TCollapseItem(name="b", title="B")
        collapse.add_item(item_a)
        collapse.add_item(item_b)
        assert item_a.expanded is False
        assert item_b.expanded is True

    def test_get_expanded_names(self, qapp: QApplication) -> None:
        collapse = TCollapse(expanded_names=["a", "c"])
        for name in ["a", "b", "c"]:
            collapse.add_item(TCollapseItem(name=name, title=name.upper()))
        assert sorted(collapse.get_expanded_names()) == ["a", "c"]

    def test_accordion_mode(self, qapp: QApplication) -> None:
        collapse = TCollapse(accordion=True)
        item_a = TCollapseItem(name="a", title="A")
        item_b = TCollapseItem(name="b", title="B")
        collapse.add_item(item_a)
        collapse.add_item(item_b)
        item_a.set_expanded(True, animate=False)
        assert item_a.expanded is True
        assert item_b.expanded is False
        item_b.set_expanded(True, animate=False)
        assert item_b.expanded is True
        assert item_a.expanded is False

    def test_non_accordion_allows_multiple(self, qapp: QApplication) -> None:
        collapse = TCollapse(accordion=False)
        item_a = TCollapseItem(name="a", title="A")
        item_b = TCollapseItem(name="b", title="B")
        collapse.add_item(item_a)
        collapse.add_item(item_b)
        item_a.set_expanded(True, animate=False)
        item_b.set_expanded(True, animate=False)
        assert item_a.expanded is True
        assert item_b.expanded is True

    def test_item_expanded_signal(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        item = TCollapseItem(name="x", title="X")
        collapse.add_item(item)
        received: list[tuple[str, bool]] = []
        collapse.item_expanded.connect(lambda n, e: received.append((n, e)))
        item.set_expanded(True, animate=False)
        assert len(received) == 1
        assert received[0] == ("x", True)

    def test_accordion_setter(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        assert collapse.accordion is False
        collapse.accordion = True
        assert collapse.accordion is True


class TestTCollapseArrowPlacement:
    """Tests for arrow_placement feature (Req 65.1)."""

    def test_default_arrow_placement(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        assert collapse.arrow_placement == "left"

    def test_arrow_placement_right_init(self, qapp: QApplication) -> None:
        collapse = TCollapse(arrow_placement="right")
        assert collapse.arrow_placement == "right"

    def test_arrow_placement_setter(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        collapse.arrow_placement = "right"
        assert collapse.arrow_placement == "right"

    def test_arrow_placement_invalid_defaults_left(self, qapp: QApplication) -> None:
        collapse = TCollapse(arrow_placement="invalid")
        assert collapse.arrow_placement == "left"

    def test_arrow_placement_propagates_to_items(self, qapp: QApplication) -> None:
        collapse = TCollapse(arrow_placement="right")
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        assert item._arrow_placement == "right"

    def test_arrow_placement_setter_updates_items(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        collapse.arrow_placement = "right"
        assert item._arrow_placement == "right"

    def test_arrow_right_layout_order(self, qapp: QApplication) -> None:
        collapse = TCollapse(arrow_placement="right")
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        layout = item._header_layout
        assert layout.itemAt(0).widget() is item._title_label
        assert layout.itemAt(1).widget() is item._arrow_label

    def test_arrow_left_layout_order(self, qapp: QApplication) -> None:
        collapse = TCollapse(arrow_placement="left")
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        layout = item._header_layout
        assert layout.itemAt(0).widget() is item._arrow_label
        assert layout.itemAt(1).widget() is item._title_label


class TestTCollapseTriggerAreas:
    """Tests for trigger_areas feature (Req 65.2-65.4)."""

    def test_default_trigger_areas(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        assert collapse.trigger_areas == ["main", "extra", "arrow"]

    def test_trigger_areas_init(self, qapp: QApplication) -> None:
        collapse = TCollapse(trigger_areas=["arrow"])
        assert collapse.trigger_areas == ["arrow"]

    def test_trigger_areas_setter(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        collapse.trigger_areas = ["arrow"]
        assert collapse.trigger_areas == ["arrow"]

    def test_trigger_areas_propagates_to_items(self, qapp: QApplication) -> None:
        collapse = TCollapse(trigger_areas=["arrow"])
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        assert item._trigger_areas == ["arrow"]

    def test_trigger_areas_setter_updates_items(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        collapse.trigger_areas = ["arrow"]
        assert item._trigger_areas == ["arrow"]

    def test_trigger_areas_filters_invalid(self, qapp: QApplication) -> None:
        collapse = TCollapse(trigger_areas=["main", "invalid", "arrow"])
        assert collapse.trigger_areas == ["main", "arrow"]


class TestTCollapseItemHeaderClicked:
    """Tests for item_header_clicked signal (Req 65.5)."""

    def test_item_header_clicked_signal_exists(self, qapp: QApplication) -> None:
        collapse = TCollapse()
        received: list[str] = []
        collapse.item_header_clicked.connect(lambda name: received.append(name))
        assert len(received) == 0


class TestTCollapseItemCustomWidgets:
    """Tests for set_title, set_header_extra, set_arrow (Req 65.6-65.8)."""

    def test_set_title_custom_widget(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        custom = QLabel("Custom Title")
        item.set_title(custom)
        assert item._custom_title_widget is custom
        assert item._title_label.isVisible() is False

    def test_set_title_replaces_previous(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        first = QLabel("First")
        second = QLabel("Second")
        item.set_title(first)
        item.set_title(second)
        assert item._custom_title_widget is second

    def test_set_header_extra(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        extra = QLabel("Extra")
        item.set_header_extra(extra)
        assert item._header_extra_widget is extra

    def test_set_header_extra_replaces(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        first = QLabel("First")
        second = QLabel("Second")
        item.set_header_extra(first)
        item.set_header_extra(second)
        assert item._header_extra_widget is second

    def test_set_arrow_custom_widget(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        custom_arrow = QLabel("→")
        item.set_arrow(custom_arrow)
        assert item._custom_arrow_widget is custom_arrow
        assert item._arrow_label.isVisible() is False

    def test_set_arrow_replaces_previous(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        first = QLabel("→")
        second = QLabel("⇒")
        item.set_arrow(first)
        item.set_arrow(second)
        assert item._custom_arrow_widget is second

    def test_custom_arrow_skips_text_update(self, qapp: QApplication) -> None:
        item = TCollapseItem(name="a", title="A")
        custom_arrow = QLabel("→")
        item.set_arrow(custom_arrow)
        item.set_expanded(True, animate=False)
        assert item.expanded is True

    def test_header_extra_in_right_arrow_layout(self, qapp: QApplication) -> None:
        collapse = TCollapse(arrow_placement="right")
        item = TCollapseItem(name="a", title="A")
        collapse.add_item(item)
        extra = QLabel("Extra")
        item.set_header_extra(extra)
        layout = item._header_layout
        assert layout.itemAt(0).widget() is item._title_label
        assert layout.itemAt(1).widget() is item._arrow_label
        assert layout.itemAt(3).widget() is extra


class TestFirstItemProperty:
    """Tests for the firstItem dynamic property used for divider styling."""

    def test_first_item_property(self, qapp: QApplication) -> None:
        """Verify firstItem property is correctly set after adding multiple items,
        and correctly updated after removal."""
        collapse = TCollapse()
        item1 = TCollapseItem(name="a", title="A")
        item2 = TCollapseItem(name="b", title="B")
        item3 = TCollapseItem(name="c", title="C")

        collapse.add_item(item1)
        collapse.add_item(item2)
        collapse.add_item(item3)

        assert item1.property("firstItem") == "true"
        assert item2.property("firstItem") == "false"
        assert item3.property("firstItem") == "false"

        # Remove the first item; item2 should become the new first
        collapse.remove_item(item1)
        assert item2.property("firstItem") == "true"
        assert item3.property("firstItem") == "false"

    def test_first_item_single(self, qapp: QApplication) -> None:
        """Verify a single item has firstItem set to 'true'."""
        collapse = TCollapse()
        item = TCollapseItem(name="only", title="Only")
        collapse.add_item(item)
        assert item.property("firstItem") == "true"


# ---------------------------------------------------------------------------
# Property-Based Tests (Hypothesis)
# ---------------------------------------------------------------------------

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st


# Feature: collapse-visual-bugfix, Property 2: 箭头旋转状态一致性
class TestArrowRotationStateProperty:
    """Property-based test: arrow widget _expanded always matches item _expanded
    after any sequence of toggle operations.

    **Validates: Requirements 2.1, 2.2**
    """

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(toggles=st.lists(st.booleans(), min_size=1, max_size=30))
    def test_arrow_expanded_matches_item_expanded(
        self, qapp: QApplication, toggles: list[bool]
    ) -> None:
        """After any sequence of toggle/set_expanded calls, the arrow widget's
        _expanded attribute must equal the item's _expanded attribute."""
        item = TCollapseItem(name="prop2", title="Prop2")

        for should_toggle in toggles:
            if should_toggle:
                item.toggle()
            else:
                # Explicitly set to the opposite of current state
                item.set_expanded(not item._expanded, animate=False)

            assert item._arrow_label._expanded == item._expanded, (
                f"Arrow _expanded={item._arrow_label._expanded} != "
                f"item _expanded={item._expanded}"
            )


# Feature: collapse-visual-bugfix, Property 3: 分割线首项排除不变量
class TestFirstItemDividerProperty:
    """Property-based test: after any sequence of add/remove operations the first
    item has firstItem='true' and all others have firstItem='false'.

    **Validates: Requirements 4.1, 4.2**
    """

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        ops=st.lists(
            st.tuples(
                st.sampled_from(["add", "remove"]),
                st.integers(min_value=0, max_value=99),
            ),
            min_size=1,
            max_size=40,
        )
    )
    def test_first_item_invariant(
        self, qapp: QApplication, ops: list[tuple[str, int]]
    ) -> None:
        """After any add/remove sequence, firstItem property is correct."""
        collapse = TCollapse()
        pool: list[TCollapseItem] = []
        counter = 0

        for action, idx in ops:
            if action == "add":
                item = TCollapseItem(name=f"item_{counter}", title=f"Item {counter}")
                counter += 1
                pool.append(item)
                collapse.add_item(item)
            elif action == "remove" and collapse.items:
                target = collapse.items[idx % len(collapse.items)]
                collapse.remove_item(target)

            # Invariant check after every operation
            items = collapse.items
            for i, it in enumerate(items):
                expected = "true" if i == 0 else "false"
                actual = it.property("firstItem")
                assert actual == expected, (
                    f"Item index {i} (name={it.item_name}): "
                    f"firstItem={actual!r}, expected={expected!r}"
                )
