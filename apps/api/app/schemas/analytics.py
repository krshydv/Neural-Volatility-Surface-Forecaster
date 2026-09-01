from datetime import date

from pydantic import BaseModel, Field


class RegimePointResponse(BaseModel):
    trade_date: date
    realized_vol: float
    regime_index: int
    regime_label: str


class RegimeDetectionResponse(BaseModel):
    symbol: str
    points: list[RegimePointResponse]
    centroids: list[float]
    current_regime: str


class ScenarioRequest(BaseModel):
    spot_shock_pct: float = Field(ge=-0.9, le=5.0)
    vol_shock_pct: float = Field(ge=-0.9, le=5.0)


class ScenarioContractResponse(BaseModel):
    symbol: str
    strike: float
    expiry: date
    option_type: str
    base_price: float
    shocked_price: float
    price_change_pct: float
    base_delta: float
    shocked_delta: float


class ScenarioResponse(BaseModel):
    symbol: str
    base_spot: float
    shocked_spot: float
    spot_shock_pct: float
    vol_shock_pct: float
    total_delta_change_pct: float
    contracts: list[ScenarioContractResponse]


class RiskExposureResponse(BaseModel):
    symbol: str
    spot: float
    contract_count: int
    net_delta: float
    net_gamma: float
    net_vega: float
    net_theta: float
    open_interest_weighted_delta: float
