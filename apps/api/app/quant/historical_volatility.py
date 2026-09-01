import math

TRADING_DAYS_PER_YEAR = 252


def log_returns(prices: list[float]) -> list[float]:
    if len(prices) < 2:
        raise ValueError("At least two prices are required to compute returns")
    if any(p <= 0 for p in prices):
        raise ValueError("Prices must be positive")

    return [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]


def _std_dev(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        raise ValueError("At least two values are required to compute standard deviation")

    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(variance)


def realized_volatility(
    prices: list[float], trading_days_per_year: int = TRADING_DAYS_PER_YEAR
) -> float:
    returns = log_returns(prices)
    daily_std = _std_dev(returns)
    return daily_std * math.sqrt(trading_days_per_year)


def rolling_realized_volatility(
    prices: list[float],
    window: int,
    trading_days_per_year: int = TRADING_DAYS_PER_YEAR,
) -> list[float]:
    if window < 2:
        raise ValueError("window must be at least 2")
    if len(prices) < window:
        raise ValueError("Not enough prices for the requested window")

    results: list[float] = []
    for end in range(window, len(prices) + 1):
        window_prices = prices[end - window : end]
        results.append(realized_volatility(window_prices, trading_days_per_year))

    return results
