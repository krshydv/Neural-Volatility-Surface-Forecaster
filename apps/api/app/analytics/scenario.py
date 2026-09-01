from dataclasses import dataclass
from datetime import date

from app.market_data.types import OptionsChainSnapshot
from app.quant.black_scholes import BlackScholesInputs, OptionType, price
from app.quant.greeks import compute_greeks

RISK_FREE_RATE = 0.045


@dataclass(frozen=True)
class ScenarioContractResult:
    symbol: str
    strike: float
    expiry: date
    option_type: str
    base_price: float
    shocked_price: float
    price_change_pct: float
    base_delta: float
    shocked_delta: float


@dataclass(frozen=True)
class ScenarioResult:
    symbol: str
    base_spot: float
    shocked_spot: float
    spot_shock_pct: float
    vol_shock_pct: float
    contracts: list[ScenarioContractResult]
    total_delta_change_pct: float


def run_scenario(
    chain: OptionsChainSnapshot,
    spot_shock_pct: float,
    vol_shock_pct: float,
) -> ScenarioResult:
    shocked_spot = chain.spot * (1 + spot_shock_pct)
    contracts: list[ScenarioContractResult] = []

    base_delta_sum = 0.0
    shocked_delta_sum = 0.0

    for c in chain.contracts:
        option_type = OptionType.CALL if c.option_type == "call" else OptionType.PUT
        expiry_years = max((c.expiry - date.today()).days / 365.0, 1 / 365.0)

        base_inputs = BlackScholesInputs(
            spot=chain.spot,
            strike=c.strike,
            time_to_expiry=expiry_years,
            risk_free_rate=RISK_FREE_RATE,
            volatility=c.implied_volatility,
        )
        shocked_inputs = BlackScholesInputs(
            spot=shocked_spot,
            strike=c.strike,
            time_to_expiry=expiry_years,
            risk_free_rate=RISK_FREE_RATE,
            volatility=max(c.implied_volatility * (1 + vol_shock_pct), 0.01),
        )

        base_price = price(base_inputs, option_type)
        shocked_price = price(shocked_inputs, option_type)
        base_greeks = compute_greeks(base_inputs, option_type)
        shocked_greeks = compute_greeks(shocked_inputs, option_type)

        price_change_pct = (
            (shocked_price - base_price) / base_price if base_price > 0 else 0.0
        )

        base_delta_sum += base_greeks.delta
        shocked_delta_sum += shocked_greeks.delta

        contracts.append(
            ScenarioContractResult(
                symbol=c.symbol,
                strike=c.strike,
                expiry=c.expiry,
                option_type=c.option_type,
                base_price=base_price,
                shocked_price=shocked_price,
                price_change_pct=price_change_pct,
                base_delta=base_greeks.delta,
                shocked_delta=shocked_greeks.delta,
            )
        )

    total_delta_change_pct = (
        (shocked_delta_sum - base_delta_sum) / abs(base_delta_sum)
        if base_delta_sum != 0
        else 0.0
    )

    return ScenarioResult(
        symbol=chain.symbol,
        base_spot=chain.spot,
        shocked_spot=shocked_spot,
        spot_shock_pct=spot_shock_pct,
        vol_shock_pct=vol_shock_pct,
        contracts=contracts,
        total_delta_change_pct=total_delta_change_pct,
    )
