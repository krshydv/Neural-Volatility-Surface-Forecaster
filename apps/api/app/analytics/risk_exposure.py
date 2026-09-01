from dataclasses import dataclass
from datetime import date

from app.market_data.types import OptionsChainSnapshot
from app.quant.black_scholes import BlackScholesInputs, OptionType
from app.quant.greeks import compute_greeks

RISK_FREE_RATE = 0.045


@dataclass(frozen=True)
class RiskExposure:
    symbol: str
    spot: float
    contract_count: int
    net_delta: float
    net_gamma: float
    net_vega: float
    net_theta: float
    open_interest_weighted_delta: float


def compute_risk_exposure(chain: OptionsChainSnapshot) -> RiskExposure:
    net_delta = net_gamma = net_vega = net_theta = 0.0
    oi_weighted_delta = 0.0

    for c in chain.contracts:
        option_type = OptionType.CALL if c.option_type == "call" else OptionType.PUT
        expiry_years = max((c.expiry - date.today()).days / 365.0, 1 / 365.0)
        inputs = BlackScholesInputs(
            spot=chain.spot,
            strike=c.strike,
            time_to_expiry=expiry_years,
            risk_free_rate=RISK_FREE_RATE,
            volatility=c.implied_volatility,
        )
        greeks = compute_greeks(inputs, option_type)

        net_delta += greeks.delta
        net_gamma += greeks.gamma
        net_vega += greeks.vega
        net_theta += greeks.theta
        oi_weighted_delta += greeks.delta * c.open_interest

    return RiskExposure(
        symbol=chain.symbol,
        spot=chain.spot,
        contract_count=len(chain.contracts),
        net_delta=net_delta,
        net_gamma=net_gamma,
        net_vega=net_vega,
        net_theta=net_theta,
        open_interest_weighted_delta=oi_weighted_delta,
    )
