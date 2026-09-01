from functools import lru_cache

from app.core.config import get_settings
from app.market_data.mock_provider import MockMarketDataProvider
from app.market_data.provider import MarketDataProvider


class UnsupportedProviderError(Exception):
    pass


@lru_cache
def get_market_data_provider() -> MarketDataProvider:
    settings = get_settings()

    if settings.market_data_provider == "mock":
        return MockMarketDataProvider()

    raise UnsupportedProviderError(
        f"Market data provider '{settings.market_data_provider}' is not yet implemented. "
        "Set MARKET_DATA_PROVIDER=mock, or implement a MarketDataProvider adapter and "
        "register it in app/market_data/factory.py."
    )
