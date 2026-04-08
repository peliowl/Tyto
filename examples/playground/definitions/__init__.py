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
        breadcrumb_props,
        button_props,
        checkbox_props,
        input_props,
        radio_props,
        searchbar_props,
        switch_props,
        tag_props,
    )

    # Atoms
    button_props.register(registry)
    checkbox_props.register(registry)
    radio_props.register(registry)
    input_props.register(registry)
    switch_props.register(registry)
    tag_props.register(registry)

    # Molecules
    searchbar_props.register(registry)
    breadcrumb_props.register(registry)
