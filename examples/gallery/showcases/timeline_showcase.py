"""TimelineShowcase: demonstrates TTimeline basic usage, status types, horizontal, size, and dashed lines."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from examples.gallery.showcases.base_showcase import BaseShowcase
from tyto_ui_lib import TTimeline, TTimelineItem


class TimelineShowcase(BaseShowcase):
    """Showcase for the TTimeline molecule component.

    Sections: basic usage, status types, horizontal, size variants, dashed connecting lines.

    Args:
        parent: Optional parent widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Basic usage
        tl = TTimeline()
        tl.add_item(TTimelineItem(title="Created", content="Project initialized", time="2024-01-01"))
        tl.add_item(TTimelineItem(title="In Progress", content="Development started", time="2024-02-15"))
        tl.add_item(TTimelineItem(title="Released", content="v1.0.0 published", time="2024-03-01"))
        self.add_section("Basic Usage", "Simple timeline with three events.", tl)

        # Status types
        tl2 = TTimeline()
        tl2.add_item(TTimelineItem(
            title="Finished", content="Completed step", status=TTimelineItem.ItemStatus.FINISHED,
        ))
        tl2.add_item(TTimelineItem(
            title="Pending", content="Awaiting review", status=TTimelineItem.ItemStatus.PENDING,
        ))
        tl2.add_item(TTimelineItem(
            title="Error", content="Build failed", status=TTimelineItem.ItemStatus.ERROR,
        ))
        tl2.add_item(TTimelineItem(
            title="Default", content="Standard node", status=TTimelineItem.ItemStatus.DEFAULT,
        ))
        self.add_section("Status Types", "Finished, pending, error, and default statuses.", tl2)

        # Horizontal mode
        tl_h = TTimeline(horizontal=True)
        tl_h.add_item(TTimelineItem(title="Step 1", content="First"))
        tl_h.add_item(TTimelineItem(title="Step 2", content="Second"))
        tl_h.add_item(TTimelineItem(title="Step 3", content="Third"))
        tl_h.setMinimumWidth(400)
        self.add_section("Horizontal", "Timeline rendered in horizontal layout.", tl_h)

        # Size variants
        self.add_section(
            "Size Variants",
            "Small, medium, and large timeline sizes.",
            self.hbox(
                self._make_sized_timeline(TTimeline.TimelineSize.SMALL, "Small"),
                self._make_sized_timeline(TTimeline.TimelineSize.MEDIUM, "Medium"),
                self._make_sized_timeline(TTimeline.TimelineSize.LARGE, "Large"),
            ),
        )

        # Dashed connecting lines
        tl_dashed = TTimeline()
        tl_dashed.add_item(TTimelineItem(
            title="Start", content="Solid line below", line_type=TTimelineItem.LineType.DEFAULT,
        ))
        tl_dashed.add_item(TTimelineItem(
            title="Middle", content="Dashed line below", line_type=TTimelineItem.LineType.DASHED,
        ))
        tl_dashed.add_item(TTimelineItem(title="End", content="Final node"))
        self.add_section("Dashed Lines", "Mix solid and dashed connecting lines.", tl_dashed)

    @staticmethod
    def _make_sized_timeline(size: TTimeline.TimelineSize, label: str) -> TTimeline:
        """Create a small timeline with the given size for demonstration."""
        tl = TTimeline(size=size)
        tl.add_item(TTimelineItem(title=f"{label} 1"))
        tl.add_item(TTimelineItem(title=f"{label} 2"))
        return tl
