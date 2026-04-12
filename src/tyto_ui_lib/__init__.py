"""Tyto UI Library - A modern PySide6 UI component library based on Atomic Design.

Provides a layered component system from atoms to organisms, powered by a
Design Token + Jinja2 + QSS theme engine with Light/Dark theme support.
"""

__version__ = "1.1.0"

# --- Core -------------------------------------------------------------------
from tyto_ui_lib.core.easing_engine import EasingEngine
from tyto_ui_lib.core.event_bus import EventBus
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.core.tokens import DesignTokenSet, TokenFileError, load_tokens_from_file

# --- Common ------------------------------------------------------------------
from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits import (
    ClickRippleMixin,
    ContainerQueryMixin,
    DisabledMixin,
    FocusGlowMixin,
    HoverEffectMixin,
)

# --- Atoms -------------------------------------------------------------------
from tyto_ui_lib.components.atoms.backtop import ListenToType, TBackTop
from tyto_ui_lib.components.atoms.button import TButton
from tyto_ui_lib.components.atoms.checkbox import TCheckbox, TCheckboxGroup
from tyto_ui_lib.components.atoms.empty import TEmpty
from tyto_ui_lib.components.atoms.input import TInput
from tyto_ui_lib.components.atoms.inputnumber import TInputNumber
from tyto_ui_lib.components.atoms.radio import TRadio, TRadioButton, TRadioGroup
from tyto_ui_lib.components.atoms.slider import SliderValue, TSlider
from tyto_ui_lib.components.atoms.spin import TSpin
from tyto_ui_lib.components.atoms.switch import TSwitch
from tyto_ui_lib.components.atoms.tag import TTag

# --- Molecules ---------------------------------------------------------------
from tyto_ui_lib.components.molecules.alert import TAlert
from tyto_ui_lib.components.molecules.breadcrumb import BreadcrumbItem, TBreadcrumb
from tyto_ui_lib.components.molecules.collapse import TCollapse, TCollapseItem
from tyto_ui_lib.components.molecules.inputgroup import TInputGroup
from tyto_ui_lib.components.molecules.popconfirm import TPopconfirm
from tyto_ui_lib.components.molecules.searchbar import TSearchBar
from tyto_ui_lib.components.molecules.timeline import TTimeline, TTimelineItem

# --- Organisms ---------------------------------------------------------------
from tyto_ui_lib.components.organisms.card import TCard
from tyto_ui_lib.components.organisms.layout import (
    Breakpoint,
    TLayout,
    TLayoutContent,
    TLayoutFooter,
    TLayoutHeader,
    TLayoutSider,
)
from tyto_ui_lib.components.organisms.menu import TMenu, TMenuItem, TMenuItemGroup
from tyto_ui_lib.components.organisms.message import (
    MessageManager,
    MessageSlot,
    MessageType,
    TMessage,
)
from tyto_ui_lib.components.organisms.modal import TModal

__all__ = [
    # Core
    "EasingEngine",
    "EventBus",
    "ThemeEngine",
    "DesignTokenSet",
    "TokenFileError",
    "load_tokens_from_file",
    # Common
    "BaseWidget",
    "ClickRippleMixin",
    "ContainerQueryMixin",
    "DisabledMixin",
    "FocusGlowMixin",
    "HoverEffectMixin",
    # Atoms
    "ListenToType",
    "SliderValue",
    "TBackTop",
    "TButton",
    "TCheckbox",
    "TCheckboxGroup",
    "TEmpty",
    "TInput",
    "TInputNumber",
    "TRadio",
    "TRadioButton",
    "TRadioGroup",
    "TSlider",
    "TSpin",
    "TSwitch",
    "TTag",
    # Molecules
    "BreadcrumbItem",
    "TAlert",
    "TBreadcrumb",
    "TCollapse",
    "TCollapseItem",
    "TInputGroup",
    "TPopconfirm",
    "TSearchBar",
    "TTimeline",
    "TTimelineItem",
    # Organisms
    "Breakpoint",
    "MessageManager",
    "MessageSlot",
    "MessageType",
    "TCard",
    "TLayout",
    "TLayoutContent",
    "TLayoutFooter",
    "TLayoutHeader",
    "TLayoutSider",
    "TMenu",
    "TMenuItem",
    "TMenuItemGroup",
    "TMessage",
    "TModal",
]
