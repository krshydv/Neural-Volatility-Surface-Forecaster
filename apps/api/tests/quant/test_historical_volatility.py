import math
import pytest

from app.quant.historical_volatility import (
    log_returns,
    realized_volatility,
    rolling_realized_volatility,
)


def test_log_returns_computed_correctly():
    prices = [100.0, 105.0, 102.0]
    returns = log_returns(prices)
    assert returns[0] == pytest.approx(math.log(105.0 / 100.0))
    assert returns[1] == pytest.approx(math.log(102.0 / 105.0))


def test_log_returns_requires_at_least_two_prices():
    with pytest.raises(ValueError):
        log_returns([100.0])


def test_log_returns_rejects_non_positive_prices():
    with pytest.raises(ValueError):
        log_returns([100.0, -5.0])


def test_realized_volatility_of_constant_prices_is_zero():
    prices = [100.0] * 30
    assert realized_volatility(prices) == pytest.approx(0.0, abs=1e-10)


def test_realized_volatility_matches_hand_computed_value():
    prices = [100.0, 101.0, 99.0, 100.5, 98.5]
    vol = realized_volatility(prices, trading_days_per_year=252)
    returns = log_returns(prices)
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    expected = math.sqrt(variance) * math.sqrt(252)
    assert vol == pytest.approx(expected, abs=1e-10)


def test_rolling_realized_volatility_produces_correct_number_of_windows():
    prices = list(range(100, 130))
    prices = [float(p) for p in prices]
    window = 10
    result = rolling_realized_volatility(prices, window)
    assert len(result) == len(prices) - window + 1


def test_rolling_realized_volatility_requires_minimum_window():
    with pytest.raises(ValueError):
        rolling_realized_volatility([100.0, 101.0], window=1)


def test_rolling_realized_volatility_requires_enough_prices():
    with pytest.raises(ValueError):
        rolling_realized_volatility([100.0, 101.0], window=5)
