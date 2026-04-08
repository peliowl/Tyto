"""Property definitions for TBreadcrumb in the Playground."""

from __future__ import annotations

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import BreadcrumbItem, TBreadcrumb


def register(registry: PropertyRegistry) -> None:
    """Register TBreadcrumb property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="separator", label="Separator", prop_type="str", default="/",
            apply=lambda w, v: (
                setattr(w, "_separator", str(v)),
                w.set_items(w.get_items()),  # rebuild with new separator
            ),
        ),
    ]

    registry.register("breadcrumb", definitions)
    registry.register_factory(
        "breadcrumb",
        lambda: TBreadcrumb(items=[
            BreadcrumbItem("Home", "/"),
            BreadcrumbItem("Settings", "/settings"),
            BreadcrumbItem("Profile", "/settings/profile"),
        ]),
    )
