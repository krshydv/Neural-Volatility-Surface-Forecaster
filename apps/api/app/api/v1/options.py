from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.market_data.factory import get_market_data_provider
from app.market_data.provider import MarketDataProvider
from app.models.user import User
from app.schemas.market_data import OptionContractResponse, OptionsChainResponse

router = APIRouter(prefix="/options", tags=["options"])


@router.get("/{symbol}/chain", response_model=OptionsChainResponse)
def get_options_chain(
    symbol: str,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    try:
        chain = provider.get_options_chain(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return OptionsChainResponse(
        symbol=chain.symbol,
        spot=chain.spot,
        as_of=chain.as_of,
        contracts=[
            OptionContractResponse(
                symbol=c.symbol,
                strike=c.strike,
                expiry=c.expiry,
                option_type=c.option_type,
                bid=c.bid,
                ask=c.ask,
                last=c.last,
                implied_volatility=c.implied_volatility,
                open_interest=c.open_interest,
                volume=c.volume,
            )
            for c in chain.contracts
        ],
    )
