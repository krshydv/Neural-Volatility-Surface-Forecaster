from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.market_data.factory import get_market_data_provider
from app.market_data.provider import MarketDataProvider
from app.models.user import User
from app.schemas.market_data import AssetResponse, MarketEventResponse, PricePointResponse

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse])
def list_assets(
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    return [
        AssetResponse(
            symbol=a.symbol, name=a.name, asset_class=a.asset_class, last_price=a.last_price
        )
        for a in provider.get_assets()
    ]


@router.get("/{symbol}", response_model=AssetResponse)
def get_asset(
    symbol: str,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    asset = provider.get_asset(symbol)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return AssetResponse(
        symbol=asset.symbol,
        name=asset.name,
        asset_class=asset.asset_class,
        last_price=asset.last_price,
    )


@router.get("/{symbol}/events", response_model=list[MarketEventResponse])
def get_asset_events(
    symbol: str,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    events = provider.get_market_events(symbol)
    return [
        MarketEventResponse(
            symbol=e.symbol, event_type=e.event_type, title=e.title, event_date=e.event_date
        )
        for e in events
    ]


@router.get("/{symbol}/prices", response_model=list[PricePointResponse])
def get_asset_prices(
    symbol: str,
    days: int = 180,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    if provider.get_asset(symbol) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    end = date.today()
    start = end - timedelta(days=days)
    prices = provider.get_historical_prices(symbol, start, end)
    return [PricePointResponse(trade_date=p.trade_date, close=p.close) for p in prices]
