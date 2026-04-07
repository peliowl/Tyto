"""Tyto UI Component Gallery - interactive preview of all components.

Run with:
    uv run python examples/gallery.py
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from tyto_ui_lib import (
    BreadcrumbItem,
    MessageManager,
    TBreadcrumb,
    TButton,
    TCheckbox,
    TInput,
    TInputGroup,
    TModal,
    TRadio,
    TRadioGroup,
    TSearchBar,
    TSwitch,
    TTag,
    ThemeEngine,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section(title: str) -> QLabel:
    """Create a styled section header label."""
    lbl = QLabel(title)
    lbl.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 16px;")
    return lbl


def _desc(text: str) -> QLabel:
    """Create a small description label."""
    lbl = QLabel(text)
    lbl.setStyleSheet("color: #667085; font-size: 12px; margin-bottom: 4px;")
    return lbl


def _hbox(*widgets: QWidget) -> QWidget:
    """Wrap widgets in a horizontal layout container."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(12)
    for w in widgets:
        layout.addWidget(w)
    layout.addStretch()
    return container


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_button_section() -> QWidget:
    """Build the Button demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Button"))
    lay.addWidget(_desc("Four types: Primary / Default / Dashed / Text"))

    btn_primary = TButton("Primary", button_type=TButton.ButtonType.PRIMARY)
    btn_default = TButton("Default", button_type=TButton.ButtonType.DEFAULT)
    btn_dashed = TButton("Dashed", button_type=TButton.ButtonType.DASHED)
    btn_text = TButton("Text", button_type=TButton.ButtonType.TEXT)
    lay.addWidget(_hbox(btn_primary, btn_default, btn_dashed, btn_text))

    lay.addWidget(_desc("Loading & Disabled states"))
    btn_loading = TButton("Loading", button_type=TButton.ButtonType.PRIMARY, loading=True)
    btn_disabled = TButton("Disabled", button_type=TButton.ButtonType.DEFAULT, disabled=True)
    lay.addWidget(_hbox(btn_loading, btn_disabled))

    return box


def _build_checkbox_section() -> QWidget:
    """Build the Checkbox demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Checkbox"))
    lay.addWidget(_desc("Three states: Unchecked / Checked / Indeterminate"))

    cb_unchecked = TCheckbox("Unchecked")
    cb_checked = TCheckbox("Checked", state=TCheckbox.CheckState.CHECKED)
    cb_indeterminate = TCheckbox("Indeterminate", state=TCheckbox.CheckState.INDETERMINATE)
    lay.addWidget(_hbox(cb_unchecked, cb_checked, cb_indeterminate))

    return box


def _build_radio_section() -> QWidget:
    """Build the Radio / RadioGroup demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Radio / RadioGroup"))
    lay.addWidget(_desc("Mutual exclusion within a group"))

    group = TRadioGroup()
    group.add_radio(TRadio("Option A", value="a"))
    group.add_radio(TRadio("Option B", value="b", checked=True))
    group.add_radio(TRadio("Option C", value="c"))
    lay.addWidget(group)

    return box


def _build_input_section() -> QWidget:
    """Build the Input demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Input"))

    lay.addWidget(_desc("Basic input"))
    lay.addWidget(TInput(placeholder="Enter text..."))

    lay.addWidget(_desc("Clearable input"))
    lay.addWidget(TInput(placeholder="Type and clear...", clearable=True))

    lay.addWidget(_desc("Password input"))
    lay.addWidget(TInput(placeholder="Password", password=True))

    return box


def _build_switch_section() -> QWidget:
    """Build the Switch demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Switch"))
    lay.addWidget(_desc("iOS/NaiveUI-style toggle"))

    sw_off = TSwitch(checked=False)
    sw_on = TSwitch(checked=True)
    sw_disabled = TSwitch(checked=False, disabled=True)
    lay.addWidget(_hbox(sw_off, sw_on, sw_disabled))

    return box


def _build_tag_section() -> QWidget:
    """Build the Tag demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Tag"))
    lay.addWidget(_desc("Color types: Default / Primary / Success / Warning / Error"))

    tags_type = _hbox(
        TTag("Default", tag_type=TTag.TagType.DEFAULT),
        TTag("Primary", tag_type=TTag.TagType.PRIMARY),
        TTag("Success", tag_type=TTag.TagType.SUCCESS),
        TTag("Warning", tag_type=TTag.TagType.WARNING),
        TTag("Error", tag_type=TTag.TagType.ERROR),
    )
    lay.addWidget(tags_type)

    lay.addWidget(_desc("Sizes: Small / Medium / Large  |  Closable"))
    tags_size = _hbox(
        TTag("Small", size=TTag.TagSize.SMALL),
        TTag("Medium", size=TTag.TagSize.MEDIUM),
        TTag("Large", size=TTag.TagSize.LARGE),
        TTag("Closable", tag_type=TTag.TagType.PRIMARY, closable=True),
    )
    lay.addWidget(tags_size)

    return box


def _build_searchbar_section() -> QWidget:
    """Build the SearchBar demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("SearchBar"))
    lay.addWidget(_desc("TInput + TButton composite"))
    lay.addWidget(TSearchBar(placeholder="Search...", clearable=True))

    return box


def _build_breadcrumb_section() -> QWidget:
    """Build the Breadcrumb demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Breadcrumb"))
    lay.addWidget(_desc("Navigation path with clickable items"))

    bc = TBreadcrumb(
        items=[
            BreadcrumbItem("Home", "/"),
            BreadcrumbItem("Components", "/components"),
            BreadcrumbItem("Breadcrumb", "/components/breadcrumb"),
        ],
        separator=" / ",
    )
    lay.addWidget(bc)

    return box


def _build_inputgroup_section() -> QWidget:
    """Build the InputGroup demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("InputGroup"))
    lay.addWidget(_desc("Compact horizontal arrangement with merged border-radius"))

    group = TInputGroup()
    group.add_widget(TInput(placeholder="https://"))
    group.add_widget(TButton("Go", button_type=TButton.ButtonType.PRIMARY))
    lay.addWidget(group)

    return box


def _build_message_section(parent: QWidget) -> QWidget:
    """Build the Message demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Message"))
    lay.addWidget(_desc("Click buttons to trigger global toast messages"))

    btn_info = TButton("Info", button_type=TButton.ButtonType.DEFAULT)
    btn_success = TButton("Success", button_type=TButton.ButtonType.PRIMARY)
    btn_warning = TButton("Warning", button_type=TButton.ButtonType.DEFAULT)
    btn_error = TButton("Error", button_type=TButton.ButtonType.DEFAULT)

    btn_info.clicked.connect(lambda: MessageManager.info("This is an info message"))
    btn_success.clicked.connect(lambda: MessageManager.success("Operation succeeded"))
    btn_warning.clicked.connect(lambda: MessageManager.warning("Please be careful"))
    btn_error.clicked.connect(lambda: MessageManager.error("Something went wrong"))

    lay.addWidget(_hbox(btn_info, btn_success, btn_warning, btn_error))

    return box


def _build_modal_section(parent: QWidget) -> QWidget:
    """Build the Modal demo section."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    lay.addWidget(_section("Modal"))
    lay.addWidget(_desc("Click to open a modal dialog"))

    modal = TModal(title="Example Modal", closable=True, mask_closable=True, parent=parent)
    modal.set_content(QLabel("This is the modal body content."))

    footer = QWidget()
    footer_lay = QHBoxLayout(footer)
    footer_lay.setContentsMargins(0, 0, 0, 0)
    cancel_btn = TButton("Cancel", button_type=TButton.ButtonType.DEFAULT)
    ok_btn = TButton("OK", button_type=TButton.ButtonType.PRIMARY)
    cancel_btn.clicked.connect(modal.close)
    ok_btn.clicked.connect(modal.close)
    footer_lay.addStretch()
    footer_lay.addWidget(cancel_btn)
    footer_lay.addWidget(ok_btn)
    modal.set_footer(footer)

    open_btn = TButton("Open Modal", button_type=TButton.ButtonType.PRIMARY)
    open_btn.clicked.connect(modal.open)
    lay.addWidget(open_btn)

    return box


# ---------------------------------------------------------------------------
# Main Gallery Window
# ---------------------------------------------------------------------------

class GalleryWindow(QWidget):
    """Main gallery window showcasing all Tyto UI components."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tyto UI Gallery")
        self.resize(800, 900)

        # Initialise theme engine
        engine = ThemeEngine.instance()
        engine.load_tokens()
        engine.switch_theme("light")

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # -- Top bar with title and theme toggle --
        topbar = QWidget()
        topbar.setStyleSheet("background: #f8f8fa; border-bottom: 1px solid #e0e0e6;")
        topbar_lay = QHBoxLayout(topbar)
        topbar_lay.setContentsMargins(24, 12, 24, 12)

        title = QLabel("Tyto UI Gallery")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        topbar_lay.addWidget(title)
        topbar_lay.addStretch()

        theme_label = QLabel("Dark Mode")
        topbar_lay.addWidget(theme_label)

        self._theme_switch = TSwitch(checked=False)
        self._theme_switch.toggled.connect(self._on_theme_toggled)
        topbar_lay.addWidget(self._theme_switch)

        root.addWidget(topbar)

        # -- Scrollable content area --
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(24, 16, 24, 24)
        self._content_layout.setSpacing(16)

        # Add all component sections
        self._content_layout.addWidget(_build_button_section())
        self._content_layout.addWidget(_build_checkbox_section())
        self._content_layout.addWidget(_build_radio_section())
        self._content_layout.addWidget(_build_input_section())
        self._content_layout.addWidget(_build_switch_section())
        self._content_layout.addWidget(_build_tag_section())
        self._content_layout.addWidget(_build_searchbar_section())
        self._content_layout.addWidget(_build_breadcrumb_section())
        self._content_layout.addWidget(_build_inputgroup_section())
        self._content_layout.addWidget(_build_message_section(self))
        self._content_layout.addWidget(_build_modal_section(self))
        self._content_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

    def _on_theme_toggled(self, dark: bool) -> None:
        """Switch between light and dark themes."""
        engine = ThemeEngine.instance()
        engine.switch_theme("dark" if dark else "light")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Launch the gallery application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = GalleryWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
