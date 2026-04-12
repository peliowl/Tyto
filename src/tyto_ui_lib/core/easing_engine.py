"""Bezier curve easing engine for UI animations.

Provides standard easing functions (cubic, quadratic) and custom cubic
bezier curve support. All functions accept normalized time t in [0.0, 1.0]
and return normalized progress in [0.0, 1.0]. Values of t outside [0, 1]
are automatically clamped.
"""

from __future__ import annotations

from collections.abc import Callable

_NEWTON_ITERATIONS = 8
_NEWTON_MIN_SLOPE = 1e-3
_SUBDIVISION_PRECISION = 1e-7
_SUBDIVISION_MAX_ITERATIONS = 10


def _clamp(t: float) -> float:
    """Clamp t to [0.0, 1.0]."""
    if t < 0.0:
        return 0.0
    if t > 1.0:
        return 1.0
    return t


class EasingEngine:
    """Bezier curve easing functions for UI animations.

    Provides standard easing functions and custom bezier curve support.
    All functions accept normalized time t in [0.0, 1.0] and return
    normalized progress in [0.0, 1.0]. Input t is clamped automatically.

    Example:
        >>> progress = EasingEngine.ease_in_out_cubic(0.5)
        >>> assert 0.0 <= progress <= 1.0

        >>> ease = EasingEngine.custom_bezier(0.25, 0.1, 0.25, 1.0)
        >>> progress = ease(0.5)
        >>> assert 0.0 <= progress <= 1.0
    """

    # -- Cubic easing functions ------------------------------------------------

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in: f(t) = t³.

        Args:
            t: Normalized time in [0.0, 1.0].

        Returns:
            Normalized progress value in [0.0, 1.0].
        """
        t = _clamp(t)
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out: f(t) = 1 - (1-t)³.

        Args:
            t: Normalized time in [0.0, 1.0].

        Returns:
            Normalized progress value in [0.0, 1.0].
        """
        t = _clamp(t)
        inv = 1.0 - t
        return 1.0 - inv * inv * inv

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out: smooth acceleration and deceleration.

        Uses 4t³ for the first half and 1 - (-2t+2)³/2 for the second half.

        Args:
            t: Normalized time in [0.0, 1.0].

        Returns:
            Normalized progress value in [0.0, 1.0].
        """
        t = _clamp(t)
        if t < 0.5:
            return 4.0 * t * t * t
        inv = -2.0 * t + 2.0
        return 1.0 - inv * inv * inv / 2.0

    # -- Quadratic easing functions --------------------------------------------

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in: f(t) = t².

        Args:
            t: Normalized time in [0.0, 1.0].

        Returns:
            Normalized progress value in [0.0, 1.0].
        """
        t = _clamp(t)
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out: f(t) = 1 - (1-t)².

        Args:
            t: Normalized time in [0.0, 1.0].

        Returns:
            Normalized progress value in [0.0, 1.0].
        """
        t = _clamp(t)
        inv = 1.0 - t
        return 1.0 - inv * inv

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out: smooth acceleration and deceleration.

        Uses 2t² for the first half and 1 - (-2t+2)²/2 for the second half.

        Args:
            t: Normalized time in [0.0, 1.0].

        Returns:
            Normalized progress value in [0.0, 1.0].
        """
        t = _clamp(t)
        if t < 0.5:
            return 2.0 * t * t
        inv = -2.0 * t + 2.0
        return 1.0 - inv * inv / 2.0

    # -- Custom cubic bezier ---------------------------------------------------

    @staticmethod
    def custom_bezier(
        p1x: float, p1y: float, p2x: float, p2y: float
    ) -> Callable[[float], float]:
        """Create a custom cubic bezier easing function.

        The bezier curve is defined by four points: (0,0), (p1x,p1y),
        (p2x,p2y), (1,1). This matches the CSS cubic-bezier() function.

        Uses Newton-Raphson iteration with binary search subdivision
        fallback for robust t-for-x solving.

        Args:
            p1x: X coordinate of the first control point (clamped to [0, 1]).
            p1y: Y coordinate of the first control point.
            p2x: X coordinate of the second control point (clamped to [0, 1]).
            p2y: Y coordinate of the second control point.

        Returns:
            Easing function accepting t in [0, 1] and returning progress.

        Example:
            >>> ease = EasingEngine.custom_bezier(0.25, 0.1, 0.25, 1.0)
            >>> ease(0.0)
            0.0
            >>> ease(1.0)
            1.0
        """
        p1x = _clamp(p1x)
        p2x = _clamp(p2x)

        # Precompute polynomial coefficients for the bezier curve.
        # B(t) = 3(1-t)²t·P1 + 3(1-t)t²·P2 + t³
        cx = 3.0 * p1x
        bx = 3.0 * (p2x - p1x) - cx
        ax = 1.0 - cx - bx

        cy = 3.0 * p1y
        by = 3.0 * (p2y - p1y) - cy
        ay = 1.0 - cy - by

        def _sample_curve_x(t: float) -> float:
            return ((ax * t + bx) * t + cx) * t

        def _sample_curve_y(t: float) -> float:
            return ((ay * t + by) * t + cy) * t

        def _sample_curve_dx(t: float) -> float:
            return (3.0 * ax * t + 2.0 * bx) * t + cx

        def _solve_t_for_x(x: float) -> float:
            """Find parameter t for a given x using Newton-Raphson + subdivision."""
            t = x
            for _ in range(_NEWTON_ITERATIONS):
                dx = _sample_curve_dx(t)
                if abs(dx) < _NEWTON_MIN_SLOPE:
                    break
                current_x = _sample_curve_x(t) - x
                t -= current_x / dx
            else:
                return t

            lo, hi = 0.0, 1.0
            t = x
            for _ in range(_SUBDIVISION_MAX_ITERATIONS):
                current_x = _sample_curve_x(t) - x
                if abs(current_x) < _SUBDIVISION_PRECISION:
                    return t
                if current_x > 0.0:
                    hi = t
                else:
                    lo = t
                t = (lo + hi) / 2.0
            return t

        def easing_fn(t: float) -> float:
            t = _clamp(t)
            if t == 0.0:
                return 0.0
            if t == 1.0:
                return 1.0
            return _sample_curve_y(_solve_t_for_x(t))

        return easing_fn
