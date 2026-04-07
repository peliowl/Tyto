"""TRadio and TRadioGroup atom components: single-select radio buttons.

TRadio provides a single radio button with a smooth ring-scale animation.
TRadioGroup manages mutual exclusion across a set of TRadio instances.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QMouseEvent, QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits.focus_glow import FocusGlowMixin
from tyto_ui_lib.common.traits.hover_effect import HoverEffectMixin
from tyto_ui_lib.core.theme_engine import ThemeEngine


class _RadioIndicator(QWidget):
    """Internal widget that paints the radio circle with a scale animation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("radio_indicator")
        self.setFixedSize(QSize(16, 16))
        self._progress: float = 0.0

        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, value: float) -> None:
        self._progress = value
        self.update()

    progress = Property(float, _get_progress, _set_progress)  # type: ignore[assignment]

    def set_checked(self, checked: bool) -> None:
        """Update the visual state with a ring-scale animation.

        Args:
            checked: True to show the inner dot, False to hide it.
        """
        target = 1.0 if checked else 0.0
        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(target)
        self._anim.start()

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        """Paint the inner filled circle scaled by current progress."""
        if self._progress <= 0.01:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        engine = ThemeEngine.instance()
        try:
            color_str = engine.get_token("colors", "primary")
            color = QColor(str(color_str))
        except (RuntimeError, KeyError):
            color = QColor("#18a058")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        max_radius = 4.0
        r = max_radius * self._progress

        painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
        painter.end()


class TRadio(
    HoverEffectMixin,
    FocusGlowMixin,
    BaseWidget,
):
    """Radio button component with ring-scale animation.

    Emits ``toggled`` when the checked state changes. Clicking an unchecked
    radio selects it. Use TRadioGroup for mutual exclusion across radios.

    Args:
        label: Text label displayed next to the radio indicator.
        value: Arbitrary value associated with this radio option.
        checked: Whether the radio starts in checked state.
        parent: Optional parent widget.

    Signals:
        toggled: Emitted with the new boolean checked state.

    Example:
        >>> radio = TRadio("Option A", value="a")
        >>> radio.toggled.connect(lambda c: print(f"Checked: {c}"))
    """

    toggled = Signal(bool)

    def __init__(
        self,
        label: str = "",
        value: Any = None,
        checked: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._init_hover_effect()
        self._init_focus_glow()

        self._checked = False
        self._value = value
        self._label_text = label

        # Layout: [indicator] [label]
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

        self._indicator = _RadioIndicator(self)
        self._layout.addWidget(self._indicator)

        self._label = QLabel(label, self)
        self._label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._layout.addWidget(self._label)
        self._layout.addStretch()

        self.setProperty("checked", False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if checked:
            self.set_checked(True)

        self.apply_theme()

    # -- Public API --

    @property
    def value(self) -> Any:
        """Return the value associated with this radio."""
        return self._value

    def is_checked(self) -> bool:
        """Return whether this radio is currently checked.

        Returns:
            True if checked, False otherwise.
        """
        return self._checked

    def set_checked(self, checked: bool) -> None:
        """Set the checked state programmatically.

        Args:
            checked: True to check, False to uncheck.
        """
        if checked == self._checked:
            return
        self._checked = checked
        self._indicator.set_checked(checked)
        self.setProperty("checked", checked)
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled.emit(checked)

    # -- Theme --

    def apply_theme(self) -> None:
        """Apply the current theme's QSS to this radio."""
        engine = ThemeEngine.instance()
        if not engine.current_theme():
            return
        try:
            qss = engine.render_qss("radio.qss.j2")
            self.setStyleSheet(qss)
        except Exception:
            pass

    # -- Events --

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle click to select this radio."""
        if event.button() == Qt.MouseButton.LeftButton and not self._checked:
            self.set_checked(True)
        super().mousePressEvent(event)

    def sizeHint(self) -> QSize:
        """Provide a reasonable default size."""
        return QSize(120, 24)


class TRadioGroup(BaseWidget):
    """Radio group manager that enforces mutual exclusion.

    Manages a collection of TRadio instances so that at most one is
    checked at any time. Emits ``selection_changed`` when the selected
    radio changes.

    Args:
        parent: Optional parent widget.

    Signals:
        selection_changed: Emitted with the value of the newly selected radio.

    Example:
        >>> group = TRadioGroup()
        >>> group.add_radio(TRadio("A", value="a"))
        >>> group.add_radio(TRadio("B", value="b"))
        >>> group.selection_changed.connect(lambda v: print(f"Selected: {v}"))
    """

    selection_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._radios: list[TRadio] = []

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

    def add_radio(self, radio: TRadio) -> None:
        """Add a radio button to this group.

        Connects the radio's toggled signal to the mutual exclusion logic.

        Args:
            radio: The TRadio instance to add.
        """
        self._radios.append(radio)
        self._layout.addWidget(radio)
        radio.toggled.connect(lambda checked, r=radio: self._on_radio_toggled(r, checked))

    def get_selected_value(self) -> Any:
        """Return the value of the currently selected radio.

        Returns:
            The value of the checked radio, or None if none is selected.
        """
        for radio in self._radios:
            if radio.is_checked():
                return radio.value
        return None

    # -- Private --

    def _on_radio_toggled(self, source: TRadio, checked: bool) -> None:
        """Handle a radio being toggled; enforce mutual exclusion.

        Args:
            source: The radio that was toggled.
            checked: The new checked state.
        """
        if not checked:
            return

        for radio in self._radios:
            if radio is not source and radio.is_checked():
                radio.set_checked(False)

        self.selection_changed.emit(source.value)
