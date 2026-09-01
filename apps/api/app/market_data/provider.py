from abc import ABC, abstractmethod
from datetime import date

from app.market_data.types import (
    AssetInfo,
    MarketEventInfo,
    OptionsChainSnapshot,
    PricePoint,
)


class MarketDataProvider(ABC):
    @abstractmethod
    def get_assets(self) -> list[AssetInfo]:
        raise NotImplementedError

    @abstractmethod
    def get_asset(self, symbol: str) -> AssetInfo | None:
        raise NotImplementedError

    @abstractmethod
    def get_historical_prices(
        self, symbol: str, start: date, end: date
    ) -> list[PricePoint]:
        raise NotImplementedError

    @abstractmethod
    def get_options_chain(self, symbol: str) -> OptionsChainSnapshot:
        raise NotImplementedError

    @abstractmethod
    def get_option_contract(
        self, symbol: str, strike: float, expiry: date, option_type: str
    ):
        raise NotImplementedError

    @abstractmethod
    def get_market_events(self, symbol: str | None = None) -> list[MarketEventInfo]:
        raise NotImplementedError
