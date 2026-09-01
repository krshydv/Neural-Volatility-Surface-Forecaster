import pytest

from app.quant.black_scholes import BlackScholesInputs, OptionType, call_price, put_price
from app.quant.greeks import compute_greeks


REFERENCE = BlackScholesInputs(
    spot=100, strike=100, time_to_expiry=1.0, risk_free_rate=0.05, volatility=0.2
)


def test_call_delta_matches_known_reference_value():
    greeks = compute_greeks(REFERENCE, OptionType.CALL)
    assert greeks.delta == pytest.approx(0.6368, abs=1e-3)


def test_put_delta_matches_known_reference_value():
    greeks = compute_greeks(REFERENCE, OptionType.PUT)
    assert greeks.delta == pytest.approx(-0.3632, abs=1e-3)


def test_gamma_is_identical_for_calls_and_puts():
    call_greeks = compute_greeks(REFERENCE, OptionType.CALL)
    put_greeks = compute_greeks(REFERENCE, OptionType.PUT)
    assert call_greeks.gamma == pytest.approx(put_greeks.gamma, abs=1e-10)


def test_vega_is_identical_for_calls_and_puts():
    call_greeks = compute_greeks(REFERENCE, OptionType.CALL)
    put_greeks = compute_greeks(REFERENCE, OptionType.PUT)
    assert call_greeks.vega == pytest.approx(put_greeks.vega, abs=1e-10)


def test_gamma_matches_known_reference_value():
    greeks = compute_greeks(REFERENCE, OptionType.CALL)
    assert greeks.gamma == pytest.approx(0.01876, abs=1e-4)


def test_vega_matches_known_reference_value():
    greeks = compute_greeks(REFERENCE, OptionType.CALL)
    assert greeks.vega == pytest.approx(0.3752, abs=1e-3)


def test_delta_via_finite_difference_matches_analytic_delta():
    bump = 0.01
    bumped_up = BlackScholesInputs(
        spot=REFERENCE.spot + bump,
        strike=REFERENCE.strike,
        time_to_expiry=REFERENCE.time_to_expiry,
        risk_free_rate=REFERENCE.risk_free_rate,
        volatility=REFERENCE.volatility,
    )
    bumped_down = BlackScholesInputs(
        spot=REFERENCE.spot - bump,
        strike=REFERENCE.strike,
        time_to_expiry=REFERENCE.time_to_expiry,
        risk_free_rate=REFERENCE.risk_free_rate,
        volatility=REFERENCE.volatility,
    )
    finite_diff_delta = (call_price(bumped_up) - call_price(bumped_down)) / (2 * bump)
    analytic_delta = compute_greeks(REFERENCE, OptionType.CALL).delta
    assert finite_diff_delta == pytest.approx(analytic_delta, abs=1e-3)


def test_zero_expiry_call_delta_is_zero_or_one():
    itm = BlackScholesInputs(
        spot=110, strike=100, time_to_expiry=0.0, risk_free_rate=0.05, volatility=0.2
    )
    otm = BlackScholesInputs(
        spot=90, strike=100, time_to_expiry=0.0, risk_free_rate=0.05, volatility=0.2
    )
    assert compute_greeks(itm, OptionType.CALL).delta == 1.0
    assert compute_greeks(otm, OptionType.CALL).delta == 0.0
