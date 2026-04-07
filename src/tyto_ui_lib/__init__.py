"""Tyto UI Library - A modern PySide6 UI component library based on Atomic Design.

Provides a layered component system from atoms to organisms, powered by a
Design Token + Jinja2 + QSS theme engine with Light/Dark theme support.
"""

__version__ = "1.0.0"

# --- Core -------------------------------------------------------------------
from tyto_ui_lib.core.theme_engine import ThemeEngine
from tyto_ui_lib.core.tokens import DesignTokenSet, TokenFileError, load_tokens_from_file

# --- Common ------------------------------------------------------------------
from tyto_ui_lib.common.base import BaseWidget
from tyto_ui_lib.common.traits import (
    ClickRippleMixin,
    DisabledMixin,
    FocusGlowMixin,
    HoverEffectMixin,
)

# --- Atoms -------------------------------------------------------------------
from tyto_ui_lib.components.atoms.button import TButton
from tyto_ui_lib.components.atoms.checkbox import TCheckbox
from tyto_ui_lib.components.atoms.input import TInput
from tyto_ui_lib.components.atoms.radio import TRadio, TRadioGroup
from tyto_ui_lib.components.atoms.switch import TSwitch
from tyto_ui_lib.components.atoms.tag import TTag

# --- Molecules ---------------------------------------------------------------
from tyto_ui_lib.components.molecules.breadcrumb import BreadcrumbItem, TBreadcrumb
from tyto_ui_lib.components.molecules.inputgroup import TInputGroup
from tyto_ui_lib.components.molecules.searchbar import TSearchBar

# --- Organisms ---------------------------------------------------------------
from tyto_ui_lib.components.organisms.message import (
    MessageManager,
    MessageSlot,
    MessageType,
    TMessage,
)
from tyto_ui_lib.components.organisms.modal import TModal

__all__ = [
    # Core
    "ThemeEngine",
    "DesignTokenSet",
    "TokenFileError",
    "load_tokens_from_file",
    # Common
    "BaseWidget",
    "ClickRippleMixin",
    "DisabledMixin",
    "FocusGlowMixin",
    "HoverEffectMixin",
    # Atoms
    "TButton",
    "TCheckbox",
    "TInput",
    "TRadio",
    "TRadioGroup",
    "TSwitch",
    "TTag",
    # Molecules
    "BreadcrumbItem",
    "TBreadcrumb",
    "TInputGroup",
    "TSearchBar",
    # Organisms
    "MessageManager",
    "MessageSlot",
    "MessageType",
    "TMessage",
    "TModal",
]
