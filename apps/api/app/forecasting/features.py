import math
from dataclasses import dataclass

import numpy as np

from app.market_data.types import PricePoint

REALIZED_VOL_WINDOW = 5
LOOKBACK_WINDOWS = 6
TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class SupervisedDataset:
    x: np.ndarray
    y: np.ndarray
    feature_mean: np.ndarray
    feature_std: np.ndarray
    target_mean: float
    target_std: float
    latest_window: np.ndarray


def _log_returns(prices: list[PricePoint]) -> np.ndarray:
    closes = np.array([p.close for p in prices], dtype=np.float64)
    return np.diff(np.log(closes))


def _rolling_realized_vol(returns: np.ndarray, window: int) -> np.ndarray:
    if len(returns) < window:
        raise ValueError("Not enough return observations for the requested window")
    out = np.empty(len(returns) - window + 1, dtype=np.float64)
    for i in range(len(out)):
        segment = returns[i : i + window]
        out[i] = float(np.std(segment, ddof=1)) * math.sqrt(TRADING_DAYS_PER_YEAR)
    return out


def build_dataset(prices: list[PricePoint]) -> SupervisedDataset:
    returns = _log_returns(prices)
    realized_vol = _rolling_realized_vol(returns, REALIZED_VOL_WINDOW)

    min_required = LOOKBACK_WINDOWS + 1
    if len(realized_vol) < min_required:
        raise ValueError("Not enough historical data to build a forecasting dataset")

    rows = []
    targets = []
    for i in range(LOOKBACK_WINDOWS, len(realized_vol)):
        window = realized_vol[i - LOOKBACK_WINDOWS : i]
        rows.append(window)
        targets.append(realized_vol[i])

    x = np.array(rows, dtype=np.float64)
    y = np.array(targets, dtype=np.float64)

    feature_mean = x.mean(axis=0)
    feature_std = x.std(axis=0)
    feature_std[feature_std < 1e-8] = 1.0

    target_mean = float(y.mean())
    target_std = float(y.std()) or 1.0

    latest_window = realized_vol[-LOOKBACK_WINDOWS:]

    return SupervisedDataset(
        x=(x - feature_mean) / feature_std,
        y=(y - target_mean) / target_std,
        feature_mean=feature_mean,
        feature_std=feature_std,
        target_mean=target_mean,
        target_std=target_std,
        latest_window=latest_window,
    )
