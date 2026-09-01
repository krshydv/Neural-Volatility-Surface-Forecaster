import math
from dataclasses import replace

from app.quant.black_scholes import BlackScholesInputs, OptionType, price
from app.quant.greeks import compute_greeks

MIN_VOLATILITY = 1e-6
MAX_VOLATILITY = 5.0
DEFAULT_TOLERANCE = 1e-8
MAX_NEWTON_ITERATIONS = 50
MAX_BRENT_ITERATIONS = 100


class ImpliedVolatilityError(Exception):
    pass


def _intrinsic_value(inputs: BlackScholesInputs, option_type: OptionType) -> float:
    s, k, r, q, t = (
        inputs.spot,
        inputs.strike,
        inputs.risk_free_rate,
        inputs.dividend_yield,
        inputs.time_to_expiry,
    )
    discounted_spot = s * math.exp(-q * t)
    discounted_strike = k * math.exp(-r * t)
    if option_type == OptionType.CALL:
        return max(discounted_spot - discounted_strike, 0.0)
    return max(discounted_strike - discounted_spot, 0.0)


def _check_arbitrage_bounds(
    market_price: float, inputs: BlackScholesInputs, option_type: OptionType
) -> None:
    if market_price < 0:
        raise ImpliedVolatilityError("Option price cannot be negative")

    intrinsic = _intrinsic_value(inputs, option_type)
    if market_price < intrinsic - 1e-6:
        raise ImpliedVolatilityError(
            "Option price violates no-arbitrage lower bound relative to intrinsic value"
        )

    upper_bound = inputs.spot if option_type == OptionType.CALL else inputs.strike
    if market_price > upper_bound + 1e-6:
        raise ImpliedVolatilityError("Option price violates no-arbitrage upper bound")


def _price_and_vega(
    inputs: BlackScholesInputs, option_type: OptionType, sigma: float
) -> tuple[float, float]:
    trial_inputs = replace(inputs, volatility=sigma)
    trial_price = price(trial_inputs, option_type)
    vega = compute_greeks(trial_inputs, option_type).vega * 100.0
    return trial_price, vega


def _newton_raphson(
    market_price: float,
    inputs: BlackScholesInputs,
    option_type: OptionType,
    initial_guess: float,
    tolerance: float,
) -> float | None:
    sigma = initial_guess

    for _ in range(MAX_NEWTON_ITERATIONS):
        trial_price, vega = _price_and_vega(inputs, option_type, sigma)
        diff = trial_price - market_price

        if abs(diff) < tolerance:
            return sigma

        if vega < 1e-10:
            return None

        sigma -= diff / vega

        if sigma <= MIN_VOLATILITY or sigma >= MAX_VOLATILITY or math.isnan(sigma):
            return None

    return None


def _brent(
    market_price: float,
    inputs: BlackScholesInputs,
    option_type: OptionType,
    tolerance: float,
) -> float:
    def objective(sigma: float) -> float:
        trial_inputs = replace(inputs, volatility=sigma)
        return price(trial_inputs, option_type) - market_price

    lower, upper = MIN_VOLATILITY, MAX_VOLATILITY
    f_lower, f_upper = objective(lower), objective(upper)

    if f_lower * f_upper > 0:
        raise ImpliedVolatilityError(
            "No implied volatility solution exists within the search bounds"
        )

    for _ in range(MAX_BRENT_ITERATIONS):
        midpoint = (lower + upper) / 2.0
        f_mid = objective(midpoint)

        if abs(f_mid) < tolerance or (upper - lower) / 2.0 < tolerance:
            return midpoint

        if f_lower * f_mid < 0:
            upper, f_upper = midpoint, f_mid
        else:
            lower, f_lower = midpoint, f_mid

    raise ImpliedVolatilityError("Brent's method failed to converge")


def implied_volatility(
    market_price: float,
    inputs: BlackScholesInputs,
    option_type: OptionType,
    initial_guess: float = 0.3,
    tolerance: float = DEFAULT_TOLERANCE,
) -> float:
    _check_arbitrage_bounds(market_price, inputs, option_type)

    if inputs.time_to_expiry == 0:
        raise ImpliedVolatilityError("Cannot solve implied volatility at zero time to expiry")

    newton_result = _newton_raphson(market_price, inputs, option_type, initial_guess, tolerance)
    if newton_result is not None:
        return newton_result

    return _brent(market_price, inputs, option_type, tolerance)
