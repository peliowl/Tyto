"""Property definitions for TTimeline in the Playground."""

from __future__ import annotations

from examples.playground.models.property_definition import PropertyDefinition
from examples.playground.models.property_registry import PropertyRegistry
from tyto_ui_lib import TTimeline, TTimelineItem


def _enum_options(enum_cls: type) -> list[tuple[object, str]]:
    """Build (value, label) pairs from a string enum."""
    return [(m.value, m.value) for m in enum_cls]


def _make_timeline() -> TTimeline:
    """Create a default TTimeline with sample items."""
    tl = TTimeline()
    tl.add_item(TTimelineItem(title="Step 1", content="First step"))
    tl.add_item(TTimelineItem(title="Step 2", content="Second step"))
    tl.add_item(TTimelineItem(title="Step 3", content="Third step"))
    return tl


def register(registry: PropertyRegistry) -> None:
    """Register TTimeline property definitions and factory."""

    definitions: list[PropertyDefinition] = [
        PropertyDefinition(
            name="mode", label="Mode", prop_type="enum",
            default=TTimeline.TimelineMode.LEFT.value,
            options=_enum_options(TTimeline.TimelineMode),
            apply=lambda w, v: setattr(w, "mode", TTimeline.TimelineMode(v)),
        ),
        PropertyDefinition(
            name="horizontal", label="Horizontal", prop_type="bool", default=False,
            apply=lambda w, v: w.set_horizontal(bool(v)),
        ),
        PropertyDefinition(
            name="size", label="Size", prop_type="enum",
            default=TTimeline.TimelineSize.MEDIUM.value,
            options=_enum_options(TTimeline.TimelineSize),
            apply=lambda w, v: w.set_size(TTimeline.TimelineSize(v)),
        ),
    ]

    registry.register("timeline", definitions)
    registry.register_factory("timeline", _make_timeline)
