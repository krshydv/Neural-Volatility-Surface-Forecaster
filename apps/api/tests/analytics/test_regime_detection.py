import pytest

from app.analytics.regime_detection import InsufficientHistoryError, detect_regimes
from app.market_data.mock_provider import MockMarketDataProvider
from datetime import date, timedelta


@pytest.fixture()
def provider():
    return MockMarketDataProvider()


def test_detect_regimes_returns_labeled_points(provider):
    prices = provider.get_historical_prices("AAPL", date.today() - timedelta(days=200), date.today())
    result = detect_regimes(prices)

    assert len(result.points) > 0
    assert result.current_regime in {"Low volatility", "Medium volatility", "High volatility"}
    assert len(result.centroids) == 3
    assert result.centroids == sorted(result.centroids)


def test_detect_regimes_raises_on_short_history():
    from app.market_data.types import PricePoint

    prices = [PricePoint(trade_date=date.today(), close=100.0) for _ in range(3)]
    with pytest.raises(InsufficientHistoryError):
        detect_regimes(prices)


def test_regime_labels_are_consistent_with_centroid_order(provider):
    prices = provider.get_historical_prices("NVDA", date.today() - timedelta(days=200), date.today())
    result = detect_regimes(prices)

    for point in result.points:
        assert 0 <= point.regime_index <= 2
