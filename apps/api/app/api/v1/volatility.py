from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.market_data.factory import get_market_data_provider
from app.market_data.provider import MarketDataProvider
from app.models.user import User
from app.quant.volatility_surface import SurfacePoint, build_surface
from app.schemas.market_data import VolatilitySurfaceRequest, VolatilitySurfaceResponse

router = APIRouter(prefix="/volatility", tags=["volatility"])


@router.post("/{symbol}/surface", response_model=VolatilitySurfaceResponse)
def build_volatility_surface(
    symbol: str,
    payload: VolatilitySurfaceRequest,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    try:
        chain = provider.get_options_chain(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    today = date.today()
    points = [
        SurfacePoint(
            strike=c.strike,
            expiry_years=max((c.expiry - today).days / 365.0, 1 / 365.0),
            implied_volatility=c.implied_volatility,
        )
        for c in chain.contracts
        if c.option_type == "call"
    ]

    try:
        surface = build_surface(
            points,
            spot=chain.spot,
            grid_resolution=payload.grid_resolution,
            method=payload.method,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return VolatilitySurfaceResponse(
        symbol=symbol,
        spot=chain.spot,
        method=surface.method,
        moneyness_grid=surface.moneyness_grid,
        expiry_grid=surface.expiry_grid,
        volatility_grid=surface.volatility_grid,
    )
