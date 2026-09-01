from app.analytics.risk_exposure import compute_risk_exposure
from app.market_data.mock_provider import MockMarketDataProvider


def test_risk_exposure_aggregates_all_contracts():
    provider = MockMarketDataProvider()
    chain = provider.get_options_chain("SPY")

    result = compute_risk_exposure(chain)

    assert result.contract_count == len(chain.contracts)
    assert result.symbol == chain.symbol
    assert isinstance(result.net_delta, float)


def test_risk_exposure_weighted_delta_uses_open_interest():
    provider = MockMarketDataProvider()
    chain = provider.get_options_chain("QQQ")

    result = compute_risk_exposure(chain)

    total_oi = sum(c.open_interest for c in chain.contracts)
    if total_oi > 0:
        assert result.open_interest_weighted_delta != 0 or result.net_delta == 0
