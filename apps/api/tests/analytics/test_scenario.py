import pytest

from app.analytics.scenario import run_scenario
from app.market_data.mock_provider import MockMarketDataProvider


@pytest.fixture()
def chain():
    provider = MockMarketDataProvider()
    return provider.get_options_chain("AAPL")


def test_scenario_no_shock_matches_base_price(chain):
    result = run_scenario(chain, spot_shock_pct=0.0, vol_shock_pct=0.0)

    for c in result.contracts:
        assert c.shocked_price == pytest.approx(c.base_price, rel=1e-6)


def test_scenario_up_shock_increases_call_prices(chain):
    result = run_scenario(chain, spot_shock_pct=0.1, vol_shock_pct=0.0)

    calls = [c for c in result.contracts if c.option_type == "call"]
    assert all(c.shocked_price >= c.base_price - 1e-6 for c in calls)


def test_scenario_reports_shocked_spot(chain):
    result = run_scenario(chain, spot_shock_pct=0.05, vol_shock_pct=0.0)

    assert result.shocked_spot == pytest.approx(result.base_spot * 1.05)


def test_scenario_vol_shock_changes_price(chain):
    baseline = run_scenario(chain, spot_shock_pct=0.0, vol_shock_pct=0.0)
    shocked = run_scenario(chain, spot_shock_pct=0.0, vol_shock_pct=0.5)

    changed = any(
        abs(a.shocked_price - b.shocked_price) > 1e-6
        for a, b in zip(baseline.contracts, shocked.contracts)
    )
    assert changed
