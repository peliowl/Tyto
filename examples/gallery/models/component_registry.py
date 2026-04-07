"""Singleton registry of gallery components."""

from __future__ import annotations

import logging
from typing import ClassVar

from examples.gallery.models.component_info import ComponentInfo

logger = logging.getLogger(__name__)

# Fixed category ordering used throughout the gallery UI.
_CATEGORY_ORDER: list[str] = ["atoms", "molecules", "organisms"]


class ComponentRegistry:
    """Central registry that holds all gallery component metadata.

    Components are registered via :meth:`register` and can be queried by
    key or category.  The registry is intentionally *not* a QObject – it
    is a plain data container consumed by the ViewModel layer.

    Example:
        >>> registry = ComponentRegistry()
        >>> registry.register(ComponentInfo("Button", "button", "atoms", factory))
        >>> registry.get_by_key("button").name
        'Button'
    """

    _instance: ClassVar[ComponentRegistry | None] = None

    def __init__(self) -> None:
        self._components: dict[str, ComponentInfo] = {}

    @classmethod
    def instance(cls) -> ComponentRegistry:
        """Return the singleton registry, creating it on first call."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton.  Primarily for testing."""
        cls._instance = None

    # -- Mutation --

    def register(self, info: ComponentInfo) -> None:
        """Register a component.  Overwrites if *key* already exists."""
        if info.key in self._components:
            logger.warning("Overwriting existing registration for key '%s'", info.key)
        self._components[info.key] = info

    # -- Queries --

    def get_by_key(self, key: str) -> ComponentInfo | None:
        """Return the :class:`ComponentInfo` for *key*, or ``None``."""
        return self._components.get(key)

    def get_by_category(self, category: str) -> list[ComponentInfo]:
        """Return all components belonging to *category*, in registration order."""
        return [c for c in self._components.values() if c.category == category]

    def categories(self) -> list[str]:
        """Return the ordered list of categories: atoms → molecules → organisms."""
        return [c for c in _CATEGORY_ORDER if any(i.category == c for i in self._components.values())]

    def all_components(self) -> list[ComponentInfo]:
        """Return every registered component in registration order."""
        return list(self._components.values())
