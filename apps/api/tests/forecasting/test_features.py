from datetime import date, timedelta

import pytest

from app.forecasting.features import build_dataset
from app.market_data.types import PricePoint


def _make_prices(n: int, start_price: float = 100.0) -> list[PricePoint]:
    import random

    rng = random.Random(11)
    prices = []
    price = start_price
    base_date = date(2024, 1, 1)
    for i in range(n):
        price *= 1 + rng.uniform(-0.02, 0.02)
        prices.append(PricePoint(trade_date=base_date + timedelta(days=i), close=price))
    return prices


def test_build_dataset_shapes_are_consistent():
    prices = _make_prices(120)
    dataset = build_dataset(prices)

    assert dataset.x.shape[0] == dataset.y.shape[0]
    assert dataset.x.shape[1] == 6
    assert dataset.latest_window.shape == (6,)


def test_build_dataset_raises_on_insufficient_history():
    prices = _make_prices(5)
    with pytest.raises(ValueError):
        build_dataset(prices)


def test_build_dataset_features_are_standardized():
    prices = _make_prices(150)
    dataset = build_dataset(prices)

    column_means = dataset.x.mean(axis=0)
    assert all(abs(m) < 1e-6 for m in column_means)
