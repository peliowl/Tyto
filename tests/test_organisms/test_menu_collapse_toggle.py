"""Unit and property-based tests for _CollapseToggleButton integration in TMenu."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tyto_ui_lib.components.organisms.menu import TMenu, TMenuItem
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


def _make_click(x: int = 5, y: int = 5) -> QMouseEvent:
    """Create a left-button mouse press event."""
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPoint(x, y),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


# ---------------------------------------------------------------------------
# Unit Tests (Task 4.1)
# ---------------------------------------------------------------------------


class TestToggleVisibilityAndModeSwitching:
    """Unit tests for toggle button visibility, chevron direction, hover, and init state.

    Covers Requirements 1.3, 1.4, 1.5, 2.3, 3.1, 3.2, 3.4, 4.2, 4.3.
    """

    def test_horizontal_mode_hides_button(self, qapp: QApplication) -> None:
        """Toggle button is hidden when TMenu is in horizontal mode (Req 1.3)."""
        menu = TMenu(mode=TMenu.MenuMode.HORIZONTAL)
        assert menu._collapse_toggle.isVisible() is False

    def test_vertical_to_horizontal_hides_button(self, qapp: QApplication) -> None:
        """Switching from vertical to horizontal hides the toggle button (Req 1.4)."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        assert menu._collapse_toggle.isVisibleTo(menu) is True
        menu.set_mode(TMenu.MenuMode.HORIZONTAL)
        assert menu._collapse_toggle.isVisibleTo(menu) is False

    def test_horizontal_to_vertical_shows_button(self, qapp: QApplication) -> None:
        """Switching from horizontal to vertical shows the toggle button (Req 1.5)."""
        menu = TMenu(mode=TMenu.MenuMode.HORIZONTAL)
        assert menu._collapse_toggle.isVisibleTo(menu) is False
        menu.set_mode(TMenu.MenuMode.VERTICAL)
        assert menu._collapse_toggle.isVisibleTo(menu) is True

    def test_chevron_direction_expanded(self, qapp: QApplication) -> None:
        """Expanded state: _collapsed is False, chevron points left (Req 3.1)."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        assert menu._collapse_toggle._collapsed is False

    def test_chevron_direction_collapsed(self, qapp: QApplication) -> None:
        """Collapsed state: _collapsed is True, chevron points right (Req 3.2)."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        menu.set_collapsed(True)
        assert menu._collapse_toggle._collapsed is True

    def test_hover_state_no_effect(self, qapp: QApplication) -> None:
        """Hover does not change visual state on enter/leave events (Req 3.4 removed)."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        btn = menu._collapse_toggle
        assert not hasattr(btn, "_hovered")
        btn.enterEvent(None)
        btn.leaveEvent(None)

    def test_init_collapsed_true(self, qapp: QApplication) -> None:
        """When TMenu is initialized with collapsed=True, button state matches (Req 4.3)."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL, collapsed=True)
        assert menu._collapse_toggle._collapsed is True

    def test_clicked_signal_calls_set_collapsed(self, qapp: QApplication) -> None:
        """Clicking the toggle button inverts collapsed state via set_collapsed (Req 2.3, 4.2)."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        assert menu.collapsed is False
        # Simulate click on the toggle button
        menu._collapse_toggle.mousePressEvent(_make_click())
        assert menu.collapsed is True
        # Click again to expand
        menu._collapse_toggle.mousePressEvent(_make_click())
        assert menu.collapsed is False


# ---------------------------------------------------------------------------
# Property-Based Tests (Task 4.2)
# ---------------------------------------------------------------------------

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st


class TestDisabledStateBlocksInteraction:
    """Property 4: Disabled state blocks toggle interaction.

    *For any* disabled TMenu in vertical mode, clicking the
    Collapse_Toggle_Button shall not change the TMenu's collapsed state.
    After re-enabling the TMenu, clicking the Collapse_Toggle_Button
    shall correctly invert the collapsed state.

    **Validates: Requirements 6.1, 6.2**
    """

    # Feature: menu-collapse-toggle, Property 4: Disabled state blocks toggle interaction
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(initial_collapsed=st.booleans())
    def test_disabled_blocks_click(
        self,
        qapp: QApplication,
        initial_collapsed: bool,
    ) -> None:
        """Clicking toggle while disabled does not change collapsed state."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        if initial_collapsed:
            menu.set_collapsed(True)

        # Disable the menu
        menu.set_disabled(True)

        state_before = menu.collapsed
        # Attempt click while disabled
        menu._collapse_toggle.mousePressEvent(_make_click())
        assert menu.collapsed == state_before, (
            f"Collapsed state changed from {state_before} while disabled"
        )

    # Feature: menu-collapse-toggle, Property 4: Disabled state blocks toggle interaction
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(initial_collapsed=st.booleans())
    def test_reenable_allows_click(
        self,
        qapp: QApplication,
        initial_collapsed: bool,
    ) -> None:
        """After re-enabling, clicking toggle correctly inverts collapsed state."""
        menu = TMenu(mode=TMenu.MenuMode.VERTICAL)
        if initial_collapsed:
            menu.set_collapsed(True)

        # Disable then re-enable
        menu.set_disabled(True)
        menu.set_disabled(False)

        state_before = menu.collapsed
        menu._collapse_toggle.mousePressEvent(_make_click())
        assert menu.collapsed is (not state_before), (
            f"Expected collapsed={not state_before} after click, got {menu.collapsed}"
        )
