"""Registry mapping component keys to their property definitions and factories."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable

from examples.playground.models.property_definition import PropertyDefinition

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class PropertyRegistry:
    """Central registry holding property definitions and component factories.

    Each component key maps to a list of :class:`PropertyDefinition` objects
    that describe its editable properties, and an optional factory callable
    that creates a default component instance for the preview panel.

    Example:
        >>> registry = PropertyRegistry()
        >>> registry.register("button", [PropertyDefinition(...)])
        >>> registry.get_definitions("button")
        [PropertyDefinition(...)]
    """

    def __init__(self) -> None:
        self._definitions: dict[str, list[PropertyDefinition]] = {}
        self._factories: dict[str, Callable[..., Any]] = {}

    def register(self, component_key: str, definitions: list[PropertyDefinition]) -> None:
        """Register property definitions for a component.

        Args:
            component_key: Unique component identifier, e.g. "button".
            definitions: List of property definitions for the component.
        """
        if component_key in self._definitions:
            logger.warning("Overwriting property definitions for key '%s'", component_key)
        self._definitions[component_key] = list(definitions)

    def get_definitions(self, component_key: str) -> list[PropertyDefinition]:
        """Return property definitions for *component_key*, or an empty list.

        Args:
            component_key: The component to look up.
        """
        return list(self._definitions.get(component_key, []))

    def register_factory(self, component_key: str, factory: Callable[..., QWidget]) -> None:
        """Register a factory callable that creates a default component instance.

        Args:
            component_key: Unique component identifier.
            factory: Callable returning a new widget instance.
        """
        self._factories[component_key] = factory

    def get_factory(self, component_key: str) -> Callable[..., QWidget] | None:
        """Return the component factory for *component_key*, or ``None``.

        Args:
            component_key: The component to look up.
        """
        return self._factories.get(component_key)
