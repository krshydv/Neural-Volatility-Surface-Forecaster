import math
from dataclasses import dataclass

from app.quant.black_scholes import BlackScholesInputs, OptionType, _norm_cdf, _norm_pdf, d1_d2


@dataclass(frozen=True)
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


def compute_greeks(inputs: BlackScholesInputs, option_type: OptionType) -> Greeks:
    s, k, t, r, sigma, q = (
        inputs.spot,
        inputs.strike,
        inputs.time_to_expiry,
        inputs.risk_free_rate,
        inputs.volatility,
        inputs.dividend_yield,
    )

    if t == 0 or sigma == 0:
        is_itm = s > k if option_type == OptionType.CALL else s < k
        delta = (1.0 if option_type == OptionType.CALL else -1.0) if is_itm else 0.0
        return Greeks(delta=delta, gamma=0.0, theta=0.0, vega=0.0, rho=0.0)

    d1, d2 = d1_d2(inputs)
    sqrt_t = math.sqrt(t)
    discounted_dividend = math.exp(-q * t)
    discounted_rate = math.exp(-r * t)
    pdf_d1 = _norm_pdf(d1)

    gamma = (discounted_dividend * pdf_d1) / (s * sigma * sqrt_t)
    vega = s * discounted_dividend * pdf_d1 * sqrt_t / 100.0

    if option_type == OptionType.CALL:
        delta = discounted_dividend * _norm_cdf(d1)
        theta = (
            -(s * discounted_dividend * pdf_d1 * sigma) / (2 * sqrt_t)
            - r * k * discounted_rate * _norm_cdf(d2)
            + q * s * discounted_dividend * _norm_cdf(d1)
        ) / 365.0
        rho = (k * t * discounted_rate * _norm_cdf(d2)) / 100.0
    else:
        delta = discounted_dividend * (_norm_cdf(d1) - 1.0)
        theta = (
            -(s * discounted_dividend * pdf_d1 * sigma) / (2 * sqrt_t)
            + r * k * discounted_rate * _norm_cdf(-d2)
            - q * s * discounted_dividend * _norm_cdf(-d1)
        ) / 365.0
        rho = (-k * t * discounted_rate * _norm_cdf(-d2)) / 100.0

    return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)
