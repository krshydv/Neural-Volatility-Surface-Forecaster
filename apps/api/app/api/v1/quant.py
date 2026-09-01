from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.quant.black_scholes import BlackScholesInputs, OptionType, call_price, put_price
from app.quant.greeks import compute_greeks
from app.quant.historical_volatility import realized_volatility
from app.quant.implied_volatility import ImpliedVolatilityError, implied_volatility
from app.schemas.quant import (
    HistoricalVolatilityRequest,
    HistoricalVolatilityResponse,
    ImpliedVolatilityRequest,
    ImpliedVolatilityResponse,
    OptionPricingRequest,
    OptionPricingResponse,
)

router = APIRouter(prefix="/quant", tags=["quant"])


@router.post("/price", response_model=OptionPricingResponse)
def price_option(
    payload: OptionPricingRequest, current_user: User = Depends(get_current_user)
):
    inputs = BlackScholesInputs(
        spot=payload.spot,
        strike=payload.strike,
        time_to_expiry=payload.time_to_expiry,
        risk_free_rate=payload.risk_free_rate,
        volatility=payload.volatility,
        dividend_yield=payload.dividend_yield,
    )
    call_greeks = compute_greeks(inputs, OptionType.CALL)
    put_greeks = compute_greeks(inputs, OptionType.PUT)

    return OptionPricingResponse(
        call_price=call_price(inputs),
        put_price=put_price(inputs),
        call_greeks=call_greeks.__dict__,
        put_greeks=put_greeks.__dict__,
    )


@router.post("/implied-volatility", response_model=ImpliedVolatilityResponse)
def solve_implied_volatility(
    payload: ImpliedVolatilityRequest, current_user: User = Depends(get_current_user)
):
    inputs = BlackScholesInputs(
        spot=payload.spot,
        strike=payload.strike,
        time_to_expiry=payload.time_to_expiry,
        risk_free_rate=payload.risk_free_rate,
        volatility=0.3,
        dividend_yield=payload.dividend_yield,
    )
    option_type = OptionType.CALL if payload.option_type == "call" else OptionType.PUT

    try:
        iv = implied_volatility(payload.market_price, inputs, option_type)
    except ImpliedVolatilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ImpliedVolatilityResponse(implied_volatility=iv)


@router.post("/historical-volatility", response_model=HistoricalVolatilityResponse)
def compute_historical_volatility(
    payload: HistoricalVolatilityRequest, current_user: User = Depends(get_current_user)
):
    try:
        vol = realized_volatility(payload.prices, payload.trading_days_per_year)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return HistoricalVolatilityResponse(realized_volatility=vol)
