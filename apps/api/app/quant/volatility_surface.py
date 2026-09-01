import math
from dataclasses import dataclass

from app.quant.interpolation import INTERPOLATION_METHODS


@dataclass(frozen=True)
class SurfacePoint:
    strike: float
    expiry_years: float
    implied_volatility: float


@dataclass(frozen=True)
class SurfaceGrid:
    moneyness_grid: list[float]
    expiry_grid: list[float]
    volatility_grid: list[list[float]]
    method: str


def moneyness(strike: float, spot: float) -> float:
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be positive")
    return strike / spot


def log_moneyness(strike: float, spot: float) -> float:
    return math.log(moneyness(strike, spot))


def normalize_points(points: list[SurfacePoint], spot: float) -> list[tuple[float, float, float]]:
    return [
        (log_moneyness(p.strike, spot), p.expiry_years, p.implied_volatility) for p in points
    ]


def build_surface(
    points: list[SurfacePoint],
    spot: float,
    moneyness_range: tuple[float, float] = (-0.5, 0.5),
    expiry_range: tuple[float, float] = (0.02, 2.0),
    grid_resolution: int = 25,
    method: str = "linear",
) -> SurfaceGrid:
    if len(points) < 4:
        raise ValueError("At least four surface points are required to build a surface")
    if method not in INTERPOLATION_METHODS:
        raise ValueError(f"Unknown interpolation method: {method}")

    normalized = normalize_points(points, spot)
    known_x = [p[0] for p in normalized]
    known_y = [p[1] for p in normalized]
    known_z = [p[2] for p in normalized]

    moneyness_grid = [
        moneyness_range[0]
        + i * (moneyness_range[1] - moneyness_range[0]) / (grid_resolution - 1)
        for i in range(grid_resolution)
    ]
    expiry_grid = [
        expiry_range[0] + i * (expiry_range[1] - expiry_range[0]) / (grid_resolution - 1)
        for i in range(grid_resolution)
    ]

    query_x: list[float] = []
    query_y: list[float] = []
    for e in expiry_grid:
        for m in moneyness_grid:
            query_x.append(m)
            query_y.append(e)

    interpolate = INTERPOLATION_METHODS[method]
    flat_result = interpolate(known_x, known_y, known_z, query_x, query_y)

    volatility_grid: list[list[float]] = []
    for row_index in range(grid_resolution):
        start = row_index * grid_resolution
        end = start + grid_resolution
        row = [max(v, 1e-4) for v in flat_result[start:end]]
        volatility_grid.append(row)

    return SurfaceGrid(
        moneyness_grid=moneyness_grid,
        expiry_grid=expiry_grid,
        volatility_grid=volatility_grid,
        method=method,
    )


def extract_smile(surface: SurfaceGrid, expiry_index: int) -> list[float]:
    if expiry_index < 0 or expiry_index >= len(surface.expiry_grid):
        raise ValueError("expiry_index out of range")
    return surface.volatility_grid[expiry_index]


def extract_term_structure(surface: SurfaceGrid, moneyness_index: int) -> list[float]:
    if moneyness_index < 0 or moneyness_index >= len(surface.moneyness_grid):
        raise ValueError("moneyness_index out of range")
    return [row[moneyness_index] for row in surface.volatility_grid]
