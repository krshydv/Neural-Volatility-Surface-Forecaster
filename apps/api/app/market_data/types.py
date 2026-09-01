from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class AssetInfo:
    symbol: str
    name: str
    asset_class: str
    last_price: float


@dataclass(frozen=True)
class PricePoint:
    trade_date: date
    close: float


@dataclass(frozen=True)
class OptionContractInfo:
    symbol: str
    strike: float
    expiry: date
    option_type: str
    bid: float
    ask: float
    last: float
    implied_volatility: float
    open_interest: int
    volume: int


@dataclass(frozen=True)
class MarketEventInfo:
    symbol: str
    event_type: str
    title: str
    event_date: date


@dataclass(frozen=True)
class OptionsChainSnapshot:
    symbol: str
    spot: float
    as_of: datetime
    contracts: list[OptionContractInfo]
