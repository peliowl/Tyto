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
    from examples.gallery.showcases.alert_showcase import AlertShowcase
    from examples.gallery.showcases.backtop_showcase import BackTopShowcase
    from examples.gallery.showcases.breadcrumb_showcase import BreadcrumbShowcase
    from examples.gallery.showcases.button_showcase import ButtonShowcase
    from examples.gallery.showcases.card_showcase import CardShowcase
    from examples.gallery.showcases.checkbox_showcase import CheckboxShowcase
    from examples.gallery.showcases.collapse_showcase import CollapseShowcase
    from examples.gallery.showcases.empty_showcase import EmptyShowcase
    from examples.gallery.showcases.input_showcase import InputShowcase
    from examples.gallery.showcases.inputgroup_showcase import InputGroupShowcase
    from examples.gallery.showcases.inputnumber_showcase import InputNumberShowcase
    from examples.gallery.showcases.layout_showcase import LayoutShowcase
    from examples.gallery.showcases.menu_showcase import MenuShowcase
    from examples.gallery.showcases.message_showcase import MessageShowcase
    from examples.gallery.showcases.modal_showcase import ModalShowcase
    from examples.gallery.showcases.popconfirm_showcase import PopconfirmShowcase
    from examples.gallery.showcases.radio_showcase import RadioShowcase
    from examples.gallery.showcases.searchbar_showcase import SearchBarShowcase
    from examples.gallery.showcases.slider_showcase import SliderShowcase
    from examples.gallery.showcases.spin_showcase import SpinShowcase
    from examples.gallery.showcases.switch_showcase import SwitchShowcase
    from examples.gallery.showcases.tag_showcase import TagShowcase
    from examples.gallery.showcases.timeline_showcase import TimelineShowcase

    # Atoms
    registry.register(ComponentInfo(name="Button", key="button", category="atoms",
                                    showcase_factory=lambda parent: ButtonShowcase(parent)))
    registry.register(ComponentInfo(name="Checkbox", key="checkbox", category="atoms",
                                    showcase_factory=lambda parent: CheckboxShowcase(parent)))
    registry.register(ComponentInfo(name="Radio", key="radio", category="atoms",
                                    showcase_factory=lambda parent: RadioShowcase(parent)))
    registry.register(ComponentInfo(name="Input", key="input", category="atoms",
                                    showcase_factory=lambda parent: InputShowcase(parent)))
    registry.register(ComponentInfo(name="InputNumber", key="inputnumber", category="atoms",
                                    showcase_factory=lambda parent: InputNumberShowcase(parent)))
    registry.register(ComponentInfo(name="Switch", key="switch", category="atoms",
                                    showcase_factory=lambda parent: SwitchShowcase(parent)))
    registry.register(ComponentInfo(name="Tag", key="tag", category="atoms",
                                    showcase_factory=lambda parent: TagShowcase(parent)))
    registry.register(ComponentInfo(name="Slider", key="slider", category="atoms",
                                    showcase_factory=lambda parent: SliderShowcase(parent)))
    registry.register(ComponentInfo(name="Spin", key="spin", category="atoms",
                                    showcase_factory=lambda parent: SpinShowcase(parent)))
    registry.register(ComponentInfo(name="Empty", key="empty", category="atoms",
                                    showcase_factory=lambda parent: EmptyShowcase(parent)))
    registry.register(ComponentInfo(name="BackTop", key="backtop", category="atoms",
                                    showcase_factory=lambda parent: BackTopShowcase(parent)))

    # Molecules
    registry.register(ComponentInfo(name="SearchBar", key="searchbar", category="molecules",
                                    showcase_factory=lambda parent: SearchBarShowcase(parent)))
    registry.register(ComponentInfo(name="Breadcrumb", key="breadcrumb", category="molecules",
                                    showcase_factory=lambda parent: BreadcrumbShowcase(parent)))
    registry.register(ComponentInfo(name="InputGroup", key="inputgroup", category="molecules",
                                    showcase_factory=lambda parent: InputGroupShowcase(parent)))
    registry.register(ComponentInfo(name="Alert", key="alert", category="molecules",
                                    showcase_factory=lambda parent: AlertShowcase(parent)))
    registry.register(ComponentInfo(name="Collapse", key="collapse", category="molecules",
                                    showcase_factory=lambda parent: CollapseShowcase(parent)))
    registry.register(ComponentInfo(name="Popconfirm", key="popconfirm", category="molecules",
                                    showcase_factory=lambda parent: PopconfirmShowcase(parent)))
    registry.register(ComponentInfo(name="Timeline", key="timeline", category="molecules",
                                    showcase_factory=lambda parent: TimelineShowcase(parent)))

    # Organisms
    registry.register(ComponentInfo(name="Message", key="message", category="organisms",
                                    showcase_factory=lambda parent: MessageShowcase(parent)))
    registry.register(ComponentInfo(name="Modal", key="modal", category="organisms",
                                    showcase_factory=lambda parent: ModalShowcase(parent)))
    registry.register(ComponentInfo(name="Layout", key="layout", category="organisms",
                                    showcase_factory=lambda parent: LayoutShowcase(parent)))
    registry.register(ComponentInfo(name="Card", key="card", category="organisms",
                                    showcase_factory=lambda parent: CardShowcase(parent)))
    registry.register(ComponentInfo(name="Menu", key="menu", category="organisms",
                                    showcase_factory=lambda parent: MenuShowcase(parent)))
