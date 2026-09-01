import math
from dataclasses import dataclass
from enum import Enum


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


@dataclass(frozen=True)
class BlackScholesInputs:
    spot: float
    strike: float
    time_to_expiry: float
    risk_free_rate: float
    volatility: float
    dividend_yield: float = 0.0


def _validate(inputs: BlackScholesInputs) -> None:
    if inputs.spot <= 0:
        raise ValueError("spot must be positive")
    if inputs.strike <= 0:
        raise ValueError("strike must be positive")
    if inputs.time_to_expiry < 0:
        raise ValueError("time_to_expiry cannot be negative")
    if inputs.volatility < 0:
        raise ValueError("volatility cannot be negative")


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def d1_d2(inputs: BlackScholesInputs) -> tuple[float, float]:
    _validate(inputs)
    s, k, t, r, sigma, q = (
        inputs.spot,
        inputs.strike,
        inputs.time_to_expiry,
        inputs.risk_free_rate,
        inputs.volatility,
        inputs.dividend_yield,
    )

    if t == 0 or sigma == 0:
        d1 = math.inf if s > k else -math.inf
        return d1, d1

    d1 = (math.log(s / k) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    return d1, d2


def price(inputs: BlackScholesInputs, option_type: OptionType) -> float:
    _validate(inputs)
    s, k, t, r, sigma, q = (
        inputs.spot,
        inputs.strike,
        inputs.time_to_expiry,
        inputs.risk_free_rate,
        inputs.volatility,
        inputs.dividend_yield,
    )

    if t == 0:
        intrinsic = max(s - k, 0.0) if option_type == OptionType.CALL else max(k - s, 0.0)
        return intrinsic

    d1, d2 = d1_d2(inputs)
    discounted_spot = s * math.exp(-q * t)
    discounted_strike = k * math.exp(-r * t)

    if option_type == OptionType.CALL:
        return discounted_spot * _norm_cdf(d1) - discounted_strike * _norm_cdf(d2)
    return discounted_strike * _norm_cdf(-d2) - discounted_spot * _norm_cdf(-d1)


def call_price(inputs: BlackScholesInputs) -> float:
    return price(inputs, OptionType.CALL)


def put_price(inputs: BlackScholesInputs) -> float:
    return price(inputs, OptionType.PUT)
