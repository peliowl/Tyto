"""Unit tests for TCard organism component."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from tyto_ui_lib.components.organisms.card import TCard
from tyto_ui_lib.core.theme_engine import ThemeEngine


@pytest.fixture(autouse=True)
def _reset_engine() -> None:
    ThemeEngine.reset()
    yield  # type: ignore[misc]
    ThemeEngine.reset()


class TestTCardCreation:
    """Tests for TCard initialization and properties."""

    def test_default_properties(self, qapp: QApplication) -> None:
        card = TCard()
        assert card.title_text == ""
        assert card.size == TCard.CardSize.MEDIUM
        assert card.hoverable is False
        assert card.bordered is True
        assert card.closable is False

    def test_custom_title(self, qapp: QApplication) -> None:
        card = TCard(title="My Card")
        assert card.title_text == "My Card"

    def test_size_small(self, qapp: QApplication) -> None:
        card = TCard(size=TCard.CardSize.SMALL)
        assert card.size == TCard.CardSize.SMALL
        assert card.property("cardSize") == "small"

    def test_size_large(self, qapp: QApplication) -> None:
        card = TCard(size=TCard.CardSize.LARGE)
        assert card.size == TCard.CardSize.LARGE
        assert card.property("cardSize") == "large"

    def test_bordered_false(self, qapp: QApplication) -> None:
        card = TCard(bordered=False)
        assert card.bordered is False
        assert card.property("bordered") == "false"

    def test_closable_true_shows_button(self, qapp: QApplication) -> None:
        card = TCard(closable=True)
        assert card.closable is True
        assert card._close_btn is not None

    def test_closable_false_hides_button(self, qapp: QApplication) -> None:
        card = TCard(closable=False)
        assert card._close_btn is None

    def test_hoverable_creates_shadow(self, qapp: QApplication) -> None:
        card = TCard(hoverable=True)
        assert card._shadow is not None

    def test_not_hoverable_no_shadow(self, qapp: QApplication) -> None:
        card = TCard(hoverable=False)
        assert card._shadow is None


class TestTCardContent:
    """Tests for set_content, set_footer, set_header_extra."""

    def test_set_content(self, qapp: QApplication) -> None:
        card = TCard()
        label = QLabel("body")
        card.set_content(label)
        assert card._body_layout.count() == 1

    def test_set_footer_makes_visible(self, qapp: QApplication) -> None:
        card = TCard()
        assert card._footer.isHidden()
        footer = QLabel("footer")
        card.set_footer(footer)
        assert not card._footer.isHidden()

    def test_set_header_extra(self, qapp: QApplication) -> None:
        card = TCard()
        extra = QLabel("extra")
        card.set_header_extra(extra)
        assert card._header_extra_layout.count() == 1
        assert not card._header.isHidden()


class TestTCardClosedSignal:
    """Tests for closed signal emission."""

    def test_close_button_emits_closed(self, qapp: QApplication) -> None:
        card = TCard(closable=True)
        received: list[bool] = []
        card.closed.connect(lambda: received.append(True))
        card._on_close_clicked()
        assert len(received) == 1

    def test_no_close_button_when_not_closable(self, qapp: QApplication) -> None:
        card = TCard(closable=False)
        received: list[bool] = []
        card.closed.connect(lambda: received.append(True))
        # No close button to click, signal should not be emitted
        assert len(received) == 0
