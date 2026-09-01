from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.analytics.regime_detection import InsufficientHistoryError, detect_regimes
from app.analytics.risk_exposure import compute_risk_exposure
from app.analytics.scenario import run_scenario
from app.api.dependencies.auth import get_current_user
from app.market_data.factory import get_market_data_provider
from app.market_data.provider import MarketDataProvider
from app.models.user import User
from app.schemas.analytics import (
    RegimeDetectionResponse,
    RegimePointResponse,
    RiskExposureResponse,
    ScenarioContractResponse,
    ScenarioRequest,
    ScenarioResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

HISTORY_DAYS = 200


@router.get("/{symbol}/regime", response_model=RegimeDetectionResponse)
def get_regime_detection(
    symbol: str,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    if provider.get_asset(symbol) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown symbol: {symbol}")

    end = date.today()
    start = end - timedelta(days=HISTORY_DAYS)
    prices = provider.get_historical_prices(symbol, start, end)

    try:
        result = detect_regimes(prices)
    except InsufficientHistoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return RegimeDetectionResponse(
        symbol=symbol.upper(),
        points=[
            RegimePointResponse(
                trade_date=p.trade_date,
                realized_vol=p.realized_vol,
                regime_index=p.regime_index,
                regime_label=p.regime_label,
            )
            for p in result.points
        ],
        centroids=result.centroids,
        current_regime=result.current_regime,
    )


@router.post("/{symbol}/scenario", response_model=ScenarioResponse)
def post_scenario(
    symbol: str,
    payload: ScenarioRequest,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    try:
        chain = provider.get_options_chain(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    result = run_scenario(chain, payload.spot_shock_pct, payload.vol_shock_pct)

    return ScenarioResponse(
        symbol=result.symbol,
        base_spot=result.base_spot,
        shocked_spot=result.shocked_spot,
        spot_shock_pct=result.spot_shock_pct,
        vol_shock_pct=result.vol_shock_pct,
        total_delta_change_pct=result.total_delta_change_pct,
        contracts=[
            ScenarioContractResponse(
                symbol=c.symbol,
                strike=c.strike,
                expiry=c.expiry,
                option_type=c.option_type,
                base_price=c.base_price,
                shocked_price=c.shocked_price,
                price_change_pct=c.price_change_pct,
                base_delta=c.base_delta,
                shocked_delta=c.shocked_delta,
            )
            for c in result.contracts
        ],
    )


@router.get("/{symbol}/risk", response_model=RiskExposureResponse)
def get_risk_exposure(
    symbol: str,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    try:
        chain = provider.get_options_chain(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    result = compute_risk_exposure(chain)

    return RiskExposureResponse(
        symbol=result.symbol,
        spot=result.spot,
        contract_count=result.contract_count,
        net_delta=result.net_delta,
        net_gamma=result.net_gamma,
        net_vega=result.net_vega,
        net_theta=result.net_theta,
        open_interest_weighted_delta=result.open_interest_weighted_delta,
    )
