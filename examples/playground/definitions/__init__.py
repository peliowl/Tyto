"""Playground property definitions for all components.

Call :func:`register_all_properties` to populate a
:class:`PropertyRegistry` with every component's property definitions
and preview factories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from examples.playground.models.property_registry import PropertyRegistry


def register_all_properties(registry: PropertyRegistry) -> None:
    """Register property definitions and factories for all components.

    Args:
        registry: The PropertyRegistry to populate.
    """
    from examples.playground.definitions import (
        alert_props,
        backtop_props,
        breadcrumb_props,
        button_props,
        card_props,
        checkbox_props,
        collapse_props,
        empty_props,
        input_props,
        inputnumber_props,
        layout_props,
        menu_props,
        message_props,
        modal_props,
        popconfirm_props,
        radio_props,
        searchbar_props,
        slider_props,
        spin_props,
        switch_props,
        tag_props,
        timeline_props,
    )

    # Atoms
    button_props.register(registry)
    checkbox_props.register(registry)
    radio_props.register(registry)
    input_props.register(registry)
    inputnumber_props.register(registry)
    switch_props.register(registry)
    tag_props.register(registry)
    slider_props.register(registry)
    spin_props.register(registry)
    empty_props.register(registry)
    backtop_props.register(registry)

    # Molecules
    searchbar_props.register(registry)
    breadcrumb_props.register(registry)
    alert_props.register(registry)
    collapse_props.register(registry)
    popconfirm_props.register(registry)
    timeline_props.register(registry)

    # Organisms
    layout_props.register(registry)
    card_props.register(registry)
    menu_props.register(registry)
    message_props.register(registry)
    modal_props.register(registry)
