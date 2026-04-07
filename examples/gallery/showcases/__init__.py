"""Gallery component showcases.

The ``register_all`` function registers every component showcase with
the given registry so the navigation menu and showcase panel can
discover them automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from examples.gallery.models.component_registry import ComponentRegistry


def register_all(registry: ComponentRegistry) -> None:
    """Register all component showcases with *registry*.

    Each component is registered with its display name, unique key,
    category tier, and a factory callable that creates the showcase widget.

    Args:
        registry: The ComponentRegistry to populate.
    """
    from examples.gallery.models.component_info import ComponentInfo
    from examples.gallery.showcases.breadcrumb_showcase import BreadcrumbShowcase
    from examples.gallery.showcases.button_showcase import ButtonShowcase
    from examples.gallery.showcases.checkbox_showcase import CheckboxShowcase
    from examples.gallery.showcases.input_showcase import InputShowcase
    from examples.gallery.showcases.inputgroup_showcase import InputGroupShowcase
    from examples.gallery.showcases.message_showcase import MessageShowcase
    from examples.gallery.showcases.modal_showcase import ModalShowcase
    from examples.gallery.showcases.radio_showcase import RadioShowcase
    from examples.gallery.showcases.searchbar_showcase import SearchBarShowcase
    from examples.gallery.showcases.switch_showcase import SwitchShowcase
    from examples.gallery.showcases.tag_showcase import TagShowcase

    # Atoms
    registry.register(ComponentInfo(name="Button", key="button", category="atoms",
                                    showcase_factory=lambda parent: ButtonShowcase(parent)))
    registry.register(ComponentInfo(name="Checkbox", key="checkbox", category="atoms",
                                    showcase_factory=lambda parent: CheckboxShowcase(parent)))
    registry.register(ComponentInfo(name="Radio", key="radio", category="atoms",
                                    showcase_factory=lambda parent: RadioShowcase(parent)))
    registry.register(ComponentInfo(name="Input", key="input", category="atoms",
                                    showcase_factory=lambda parent: InputShowcase(parent)))
    registry.register(ComponentInfo(name="Switch", key="switch", category="atoms",
                                    showcase_factory=lambda parent: SwitchShowcase(parent)))
    registry.register(ComponentInfo(name="Tag", key="tag", category="atoms",
                                    showcase_factory=lambda parent: TagShowcase(parent)))

    # Molecules
    registry.register(ComponentInfo(name="SearchBar", key="searchbar", category="molecules",
                                    showcase_factory=lambda parent: SearchBarShowcase(parent)))
    registry.register(ComponentInfo(name="Breadcrumb", key="breadcrumb", category="molecules",
                                    showcase_factory=lambda parent: BreadcrumbShowcase(parent)))
    registry.register(ComponentInfo(name="InputGroup", key="inputgroup", category="molecules",
                                    showcase_factory=lambda parent: InputGroupShowcase(parent)))

    # Organisms
    registry.register(ComponentInfo(name="Message", key="message", category="organisms",
                                    showcase_factory=lambda parent: MessageShowcase(parent)))
    registry.register(ComponentInfo(name="Modal", key="modal", category="organisms",
                                    showcase_factory=lambda parent: ModalShowcase(parent)))
