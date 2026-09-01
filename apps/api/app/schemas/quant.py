from pydantic import BaseModel, Field


class OptionPricingRequest(BaseModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    time_to_expiry: float = Field(ge=0)
    risk_free_rate: float
    volatility: float = Field(ge=0)
    dividend_yield: float = 0.0


class OptionPricingResponse(BaseModel):
    call_price: float
    put_price: float
    call_greeks: dict
    put_greeks: dict


class ImpliedVolatilityRequest(BaseModel):
    market_price: float = Field(gt=0)
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    time_to_expiry: float = Field(gt=0)
    risk_free_rate: float
    dividend_yield: float = 0.0
    option_type: str = Field(pattern="^(call|put)$")


class ImpliedVolatilityResponse(BaseModel):
    implied_volatility: float


class HistoricalVolatilityRequest(BaseModel):
    prices: list[float] = Field(min_length=2)
    trading_days_per_year: int = 252


class HistoricalVolatilityResponse(BaseModel):
    realized_volatility: float
