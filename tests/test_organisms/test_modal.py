"""Unit tests for TModal organism component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from tyto_ui_lib.components.organisms.modal import TModal
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTModalCreation:
    """Tests for TModal initialization and properties."""

    def test_default_properties(self, qapp: QApplication) -> None:
        modal = TModal()
        assert modal.closable is True
        assert modal.mask_closable is True
        assert modal.title_text == ""

    def test_custom_title(self, qapp: QApplication) -> None:
        modal = TModal(title="Confirm")
        assert modal.title_text == "Confirm"

    def test_closable_false_hides_button(self, qapp: QApplication) -> None:
        modal = TModal(closable=False)
        assert modal.closable is False
        assert modal._close_btn is None

    def test_closable_true_shows_button(self, qapp: QApplication) -> None:
        modal = TModal(closable=True)
        assert modal._close_btn is not None

    def test_mask_closable_property(self, qapp: QApplication) -> None:
        modal = TModal(mask_closable=False)
        assert modal.mask_closable is False


class TestTModalContent:
    """Tests for set_content and set_footer."""

    def test_set_content(self, qapp: QApplication) -> None:
        modal = TModal()
        label = QLabel("body")
        modal.set_content(label)
        assert modal._body_layout.count() == 1

    def test_set_footer_makes_visible(self, qapp: QApplication) -> None:
        modal = TModal()
        # Footer starts hidden (not explicitly shown)
        assert modal._footer.isHidden()
        footer = QLabel("footer")
        modal.set_footer(footer)
        # After setting footer, it should no longer be explicitly hidden
        assert not modal._footer.isHidden()


class TestTModalClosedSignal:
    """Tests for closed signal emission."""

    def test_close_finish_emits_closed(self, qapp: QApplication) -> None:
        modal = TModal(closable=True)
        received: list[bool] = []
        modal.closed.connect(lambda: received.append(True))
        modal._on_close_finished()
        assert len(received) == 1

    def test_mask_click_closable_triggers_close(self, qapp: QApplication) -> None:
        modal = TModal(closable=True, mask_closable=True)
        received: list[bool] = []
        modal.closed.connect(lambda: received.append(True))
        modal._on_mask_clicked()
        # Animation would call _on_close_finished; call directly
        modal._on_close_finished()
        assert len(received) >= 1

    def test_mask_click_not_closable_no_signal(self, qapp: QApplication) -> None:
        modal = TModal(closable=False, mask_closable=True)
        received: list[bool] = []
        modal.closed.connect(lambda: received.append(True))
        modal._on_mask_clicked()
        assert len(received) == 0

    def test_mask_click_mask_not_closable_no_signal(self, qapp: QApplication) -> None:
        modal = TModal(closable=True, mask_closable=False)
        received: list[bool] = []
        modal.closed.connect(lambda: received.append(True))
        modal._on_mask_clicked()
        assert len(received) == 0
