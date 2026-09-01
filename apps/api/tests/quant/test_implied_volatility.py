import pytest

from app.quant.black_scholes import BlackScholesInputs, OptionType, call_price, put_price
from app.quant.implied_volatility import ImpliedVolatilityError, implied_volatility


def test_recovers_known_volatility_from_generated_call_price():
    true_vol = 0.25
    inputs = BlackScholesInputs(
        spot=100, strike=105, time_to_expiry=0.5, risk_free_rate=0.04, volatility=true_vol
    )
    market_price = call_price(inputs)

    solved = implied_volatility(market_price, inputs, OptionType.CALL)
    assert solved == pytest.approx(true_vol, abs=1e-4)


def test_recovers_known_volatility_from_generated_put_price():
    true_vol = 0.35
    inputs = BlackScholesInputs(
        spot=95, strike=100, time_to_expiry=1.0, risk_free_rate=0.03, volatility=true_vol
    )
    market_price = put_price(inputs)

    solved = implied_volatility(market_price, inputs, OptionType.PUT)
    assert solved == pytest.approx(true_vol, abs=1e-4)


def test_recovers_volatility_for_deep_otm_option_via_brent_fallback():
    true_vol = 0.6
    inputs = BlackScholesInputs(
        spot=100, strike=200, time_to_expiry=0.1, risk_free_rate=0.02, volatility=true_vol
    )
    market_price = call_price(inputs)

    solved = implied_volatility(market_price, inputs, OptionType.CALL, initial_guess=0.05)
    assert solved == pytest.approx(true_vol, abs=1e-3)


def test_negative_price_raises():
    inputs = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    with pytest.raises(ImpliedVolatilityError):
        implied_volatility(-5.0, inputs, OptionType.CALL)


def test_price_below_intrinsic_value_raises():
    inputs = BlackScholesInputs(
        spot=150, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    with pytest.raises(ImpliedVolatilityError):
        implied_volatility(10.0, inputs, OptionType.CALL)


def test_price_above_upper_bound_raises():
    inputs = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
    )
    with pytest.raises(ImpliedVolatilityError):
        implied_volatility(150.0, inputs, OptionType.CALL)


def test_zero_time_to_expiry_raises():
    inputs = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=0.0, risk_free_rate=0.05, volatility=0.2
    )
    with pytest.raises(ImpliedVolatilityError):
        implied_volatility(5.0, inputs, OptionType.CALL)


@pytest.mark.parametrize("true_vol", [0.05, 0.15, 0.3, 0.5, 0.9, 1.5])
def test_recovers_volatility_across_wide_range(true_vol):
    inputs = BlackScholesInputs(
        spot=100, strike=100, time_to_expiry=0.75, risk_free_rate=0.04, volatility=true_vol
    )
    market_price = call_price(inputs)
    solved = implied_volatility(market_price, inputs, OptionType.CALL)
    assert solved == pytest.approx(true_vol, abs=1e-3)
