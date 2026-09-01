import math
from dataclasses import dataclass
from datetime import date

import numpy as np

from app.market_data.types import PricePoint

REGIME_LABELS = ["Low volatility", "Medium volatility", "High volatility"]
TRADING_DAYS_PER_YEAR = 252
ROLLING_WINDOW = 5


@dataclass(frozen=True)
class RegimePoint:
    trade_date: date
    realized_vol: float
    regime_index: int
    regime_label: str


@dataclass(frozen=True)
class RegimeResult:
    points: list[RegimePoint]
    centroids: list[float]
    current_regime: str


class InsufficientHistoryError(ValueError):
    pass


def _kmeans_1d(values: np.ndarray, k: int, seed: int = 42, iterations: int = 100) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    quantiles = np.linspace(0.1, 0.9, k)
    centroids = np.quantile(values, quantiles)

    assignments = np.zeros(len(values), dtype=int)
    for _ in range(iterations):
        distances = np.abs(values.reshape(-1, 1) - centroids.reshape(1, -1))
        new_assignments = distances.argmin(axis=1)
        if np.array_equal(new_assignments, assignments) and _ > 0:
            assignments = new_assignments
            break
        assignments = new_assignments
        for cluster in range(k):
            members = values[assignments == cluster]
            if len(members) > 0:
                centroids[cluster] = members.mean()

    return assignments, centroids


def detect_regimes(prices: list[PricePoint], k: int = 3) -> RegimeResult:
    if len(prices) < ROLLING_WINDOW + 5:
        raise InsufficientHistoryError("Not enough historical data to detect regimes")

    closes = np.array([p.close for p in prices], dtype=np.float64)
    dates = [p.trade_date for p in prices]
    returns = np.diff(np.log(closes))

    realized_vol = np.empty(len(returns) - ROLLING_WINDOW + 1, dtype=np.float64)
    for i in range(len(realized_vol)):
        segment = returns[i : i + ROLLING_WINDOW]
        realized_vol[i] = float(np.std(segment, ddof=1)) * math.sqrt(TRADING_DAYS_PER_YEAR)

    assignments, centroids = _kmeans_1d(realized_vol, k=k)

    order = np.argsort(centroids)
    rank_of_cluster = {cluster: rank for rank, cluster in enumerate(order)}

    point_dates = dates[ROLLING_WINDOW:]
    points = [
        RegimePoint(
            trade_date=point_dates[i],
            realized_vol=float(realized_vol[i]),
            regime_index=rank_of_cluster[assignments[i]],
            regime_label=REGIME_LABELS[rank_of_cluster[assignments[i]]],
        )
        for i in range(len(realized_vol))
    ]

    sorted_centroids = [float(centroids[c]) for c in order]

    return RegimeResult(
        points=points,
        centroids=sorted_centroids,
        current_regime=points[-1].regime_label,
    )
