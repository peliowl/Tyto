"""Unit tests for EasingEngine."""

from tyto_ui_lib.core.easing_engine import EasingEngine


class TestEasingEngineBoundaries:
    """Verify boundary conditions f(0)=0 and f(1)=1 for all standard functions."""

    def test_ease_in_cubic_boundaries(self) -> None:
        assert EasingEngine.ease_in_cubic(0.0) == 0.0
        assert EasingEngine.ease_in_cubic(1.0) == 1.0

    def test_ease_out_cubic_boundaries(self) -> None:
        assert EasingEngine.ease_out_cubic(0.0) == 0.0
        assert EasingEngine.ease_out_cubic(1.0) == 1.0

    def test_ease_in_out_cubic_boundaries(self) -> None:
        assert EasingEngine.ease_in_out_cubic(0.0) == 0.0
        assert EasingEngine.ease_in_out_cubic(1.0) == 1.0

    def test_ease_in_quad_boundaries(self) -> None:
        assert EasingEngine.ease_in_quad(0.0) == 0.0
        assert EasingEngine.ease_in_quad(1.0) == 1.0

    def test_ease_out_quad_boundaries(self) -> None:
        assert EasingEngine.ease_out_quad(0.0) == 0.0
        assert EasingEngine.ease_out_quad(1.0) == 1.0

    def test_ease_in_out_quad_boundaries(self) -> None:
        assert EasingEngine.ease_in_out_quad(0.0) == 0.0
        assert EasingEngine.ease_in_out_quad(1.0) == 1.0


class TestEasingEngineKnownValues:
    """Verify known mathematical values at t=0.5."""

    def test_ease_in_cubic_midpoint(self) -> None:
        assert EasingEngine.ease_in_cubic(0.5) == 0.125

    def test_ease_out_cubic_midpoint(self) -> None:
        assert EasingEngine.ease_out_cubic(0.5) == 0.875

    def test_ease_in_out_cubic_midpoint(self) -> None:
        assert EasingEngine.ease_in_out_cubic(0.5) == 0.5

    def test_ease_in_quad_midpoint(self) -> None:
        assert EasingEngine.ease_in_quad(0.5) == 0.25

    def test_ease_out_quad_midpoint(self) -> None:
        assert EasingEngine.ease_out_quad(0.5) == 0.75

    def test_ease_in_out_quad_midpoint(self) -> None:
        assert EasingEngine.ease_in_out_quad(0.5) == 0.5


class TestEasingEngineClamping:
    """Verify that t values outside [0, 1] are clamped."""

    def test_negative_t_clamped_to_zero(self) -> None:
        assert EasingEngine.ease_in_cubic(-0.5) == 0.0
        assert EasingEngine.ease_out_quad(-1.0) == 0.0

    def test_t_above_one_clamped_to_one(self) -> None:
        assert EasingEngine.ease_in_cubic(1.5) == 1.0
        assert EasingEngine.ease_out_quad(2.0) == 1.0


class TestCustomBezier:
    """Verify custom_bezier function."""

    def test_custom_bezier_boundaries(self) -> None:
        ease = EasingEngine.custom_bezier(0.25, 0.1, 0.25, 1.0)
        assert ease(0.0) == 0.0
        assert ease(1.0) == 1.0

    def test_custom_bezier_linear(self) -> None:
        """Linear bezier (0,0,1,1) should approximate identity."""
        ease = EasingEngine.custom_bezier(0.0, 0.0, 1.0, 1.0)
        for i in range(11):
            t = i / 10.0
            assert abs(ease(t) - t) < 0.01

    def test_custom_bezier_clamping(self) -> None:
        ease = EasingEngine.custom_bezier(0.25, 0.1, 0.25, 1.0)
        assert ease(-1.0) == 0.0
        assert ease(2.0) == 1.0

    def test_custom_bezier_output_in_range(self) -> None:
        """Standard CSS ease curve should produce values in [0, 1]."""
        ease = EasingEngine.custom_bezier(0.25, 0.1, 0.25, 1.0)
        for i in range(101):
            t = i / 100.0
            result = ease(t)
            assert 0.0 <= result <= 1.0, f"ease({t}) = {result} out of range"
