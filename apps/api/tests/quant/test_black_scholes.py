import math
import pytest

from app.quant.black_scholes import BlackScholesInputs, OptionType, call_price, put_price


def test_call_price_matches_known_reference_value():
    inputs = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    assert call_price(inputs) == pytest.approx(10.4506, abs=1e-3)


def test_put_price_matches_known_reference_value():
    inputs = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    assert put_price(inputs) == pytest.approx(5.5735, abs=1e-3)


def test_put_call_parity_holds():
    inputs = BlackScholesInputs(
        spot=105, strike=100, time_to_expiry=0.5, risk_free_rate=0.03, volatility=0.25
    )
    c = call_price(inputs)
    p = put_price(inputs)

    lhs = c - p
    rhs = inputs.spot - inputs.strike * math.exp(-inputs.risk_free_rate * inputs.time_to_expiry)
    assert lhs == pytest.approx(rhs, abs=1e-8)


def test_call_price_at_zero_expiry_equals_intrinsic_value():
    inputs = BlackScholesInputs(
        spot=110, strike=100, time_to_expiry=0.0, risk_free_rate=0.05, volatility=0.2
    )
    assert call_price(inputs) == pytest.approx(10.0, abs=1e-8)


def test_put_price_at_zero_expiry_equals_intrinsic_value():
    inputs = BlackScholesInputs(
        spot=90, strike=100, time_to_expiry=0.0, risk_free_rate=0.05, volatility=0.2
    )
    assert put_price(inputs) == pytest.approx(10.0, abs=1e-8)


def test_deep_itm_call_approaches_forward_intrinsic():
    inputs = BlackScholesInputs(
        spot=1000, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    price_val = call_price(inputs)
    forward_intrinsic = inputs.spot - inputs.strike * math.exp(
        -inputs.risk_free_rate * inputs.time_to_expiry
    )
    assert price_val == pytest.approx(forward_intrinsic, abs=1e-6)


def test_deep_otm_call_approaches_zero():
    inputs = BlackScholesInputs(
        spot=10, strike=1000, time_to_expiry=0.25, risk_free_rate=0.05, volatility=0.2
    )
    assert call_price(inputs) < 1e-6


def test_negative_spot_raises():
    with pytest.raises(ValueError):
        call_price(
            BlackScholesInputs(
                spot=-10, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
            )
        )


def test_negative_strike_raises():
    with pytest.raises(ValueError):
        call_price(
            BlackScholesInputs(
                spot=100, strike=-10, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
            )
        )


def test_negative_time_raises():
    with pytest.raises(ValueError):
        call_price(
            BlackScholesInputs(
                spot=100, strike=100, time_to_expiry=-1.0, risk_free_rate=0.05, volatility=0.2
            )
        )


def test_dividend_yield_reduces_call_price():
    base = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    with_dividend = BlackScholesInputs(
        spot=100,
        strike=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        dividend_yield=0.03,
    )
    assert call_price(with_dividend) < call_price(base)
