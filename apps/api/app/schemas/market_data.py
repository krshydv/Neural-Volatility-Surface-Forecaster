from datetime import date, datetime

from pydantic import BaseModel


class AssetResponse(BaseModel):
    symbol: str
    name: str
    asset_class: str
    last_price: float


class PricePointResponse(BaseModel):
    trade_date: date
    close: float


class OptionContractResponse(BaseModel):
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


class OptionsChainResponse(BaseModel):
    symbol: str
    spot: float
    as_of: datetime
    contracts: list[OptionContractResponse]


class MarketEventResponse(BaseModel):
    symbol: str
    event_type: str
    title: str
    event_date: date


class VolatilitySurfaceRequest(BaseModel):
    method: str = "linear"
    grid_resolution: int = 25


class VolatilitySurfaceResponse(BaseModel):
    symbol: str
    spot: float
    method: str
    moneyness_grid: list[float]
    expiry_grid: list[float]
    volatility_grid: list[list[float]]
