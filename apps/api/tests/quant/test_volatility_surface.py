import pytest

from app.quant.volatility_surface import (
    SurfacePoint,
    build_surface,
    extract_smile,
    extract_term_structure,
    log_moneyness,
    moneyness,
)


def test_moneyness_computed_correctly():
    assert moneyness(strike=110, spot=100) == pytest.approx(1.1)


def test_moneyness_rejects_non_positive_values():
    with pytest.raises(ValueError):
        moneyness(strike=-10, spot=100)


def _synthetic_points() -> list[SurfacePoint]:
    points = []
    for expiry in [0.1, 0.25, 0.5, 1.0]:
        for strike in [80, 90, 100, 110, 120]:
            skew_adjustment = (100 - strike) * 0.0005
            base_vol = 0.2 + skew_adjustment + expiry * 0.01
            points.append(SurfacePoint(strike=strike, expiry_years=expiry, implied_volatility=base_vol))
    return points


def test_build_surface_returns_correct_grid_shape():
    points = _synthetic_points()
    surface = build_surface(points, spot=100, grid_resolution=10, method="linear")
    assert len(surface.moneyness_grid) == 10
    assert len(surface.expiry_grid) == 10
    assert len(surface.volatility_grid) == 10
    assert all(len(row) == 10 for row in surface.volatility_grid)


def test_build_surface_requires_minimum_points():
    with pytest.raises(ValueError):
        build_surface(
            [SurfacePoint(strike=100, expiry_years=0.5, implied_volatility=0.2)],
            spot=100,
        )


def test_build_surface_rejects_unknown_method():
    with pytest.raises(ValueError):
        build_surface(_synthetic_points(), spot=100, method="not_a_real_method")


def test_all_interpolation_methods_produce_positive_volatilities():
    points = _synthetic_points()
    for method in ["linear", "cubic", "rbf"]:
        surface = build_surface(points, spot=100, grid_resolution=8, method=method)
        for row in surface.volatility_grid:
            for vol in row:
                assert vol > 0


def test_extract_smile_returns_correct_row():
    points = _synthetic_points()
    surface = build_surface(points, spot=100, grid_resolution=10, method="linear")
    smile = extract_smile(surface, expiry_index=3)
    assert smile == surface.volatility_grid[3]


def test_extract_smile_rejects_out_of_range_index():
    points = _synthetic_points()
    surface = build_surface(points, spot=100, grid_resolution=10, method="linear")
    with pytest.raises(ValueError):
        extract_smile(surface, expiry_index=999)


def test_extract_term_structure_returns_correct_column():
    points = _synthetic_points()
    surface = build_surface(points, spot=100, grid_resolution=10, method="linear")
    term_structure = extract_term_structure(surface, moneyness_index=2)
    expected = [row[2] for row in surface.volatility_grid]
    assert term_structure == expected
