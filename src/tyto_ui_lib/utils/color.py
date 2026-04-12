"""Color parsing utilities for Design Token values.

Provides helpers to convert CSS color strings (including rgba() format)
into QColor objects, since Qt's QColor constructor does not natively
support the CSS ``rgba(r, g, b, a)`` syntax.
"""

from __future__ import annotations

import re

from PySide6.QtGui import QColor

_RGBA_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)"
)

_RGB_RE = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def parse_color(value: str, fallback: str = "#000000") -> QColor:
    """Parse a CSS color string into a QColor.

    Supports hex (#RGB, #RRGGBB, #AARRGGBB), named colors, and
    ``rgba(r, g, b, a)`` / ``rgb(r, g, b)`` format where *a* is a
    float in [0, 1].

    Args:
        value: CSS color string.
        fallback: Fallback color if parsing fails.

    Returns:
        Parsed QColor instance.
    """
    value = value.strip()
    m = _RGBA_RE.match(value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        color = QColor(r, g, b)
        color.setAlphaF(min(max(a, 0.0), 1.0))
        return color

    m2 = _RGB_RE.match(value)
    if m2:
        return QColor(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))

    color = QColor(value)
    if color.isValid():
        return color
    return QColor(fallback)
