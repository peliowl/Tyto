"""Property-based tests for TCheckboxGroup component."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.atoms.checkbox import TCheckbox, TCheckboxGroup
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestCheckboxGroupConstraint:
    """Property-based tests for CheckboxGroup min/max selection constraints."""

    # Feature: tyto-ui-lib-v1, Property 53: CheckboxGroup 选中数量约束
    # **Validates: Requirements 33.8**
    @settings(max_examples=100, deadline=None)
    @given(max_sel=st.integers(min_value=1, max_value=4))
    def test_max_constraint(self, qapp: QApplication, max_sel: int) -> None:
        group = TCheckboxGroup(max=max_sel)
        cbs: list[TCheckbox] = []
        for i in range(5):
            cb = TCheckbox(f"Item {i}", value=f"v{i}")
            group.add_checkbox(cb)
            cbs.append(cb)

        # Try to check all — only max_sel should succeed
        for cb in cbs:
            if cb.get_state() != TCheckbox.CheckState.CHECKED:
                cb.toggle()

        checked = sum(1 for cb in cbs if cb.get_state() == TCheckbox.CheckState.CHECKED)
        assert checked <= max_sel


class TestCheckboxGroupValueConsistency:
    """Property-based tests for CheckboxGroup value consistency."""

    # Feature: tyto-ui-lib-v1, Property 54: CheckboxGroup value 一致性
    # **Validates: Requirements 33.7**
    @settings(max_examples=100, deadline=None)
    @given(indices=st.lists(st.integers(min_value=0, max_value=4), min_size=0, max_size=5, unique=True))
    def test_get_value_matches_checked(self, qapp: QApplication, indices: list[int]) -> None:
        group = TCheckboxGroup()
        values = ["a", "b", "c", "d", "e"]
        cbs: list[TCheckbox] = []
        for v in values:
            cb = TCheckbox(v, value=v)
            group.add_checkbox(cb)
            cbs.append(cb)

        # Programmatically set values
        selected = [values[i] for i in indices]
        group.set_value(selected)

        # get_value should match the set of checked checkbox values
        result = group.get_value()
        assert sorted(result) == sorted(selected)
