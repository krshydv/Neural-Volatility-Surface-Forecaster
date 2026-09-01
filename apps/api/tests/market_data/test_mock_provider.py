from datetime import date, timedelta

import pytest

from app.market_data.mock_provider import MockMarketDataProvider


@pytest.fixture()
def provider():
    return MockMarketDataProvider()


def test_get_assets_returns_registry(provider):
    assets = provider.get_assets()
    symbols = {a.symbol for a in assets}
    assert "AAPL" in symbols
    assert "NVDA" in symbols
    assert len(assets) >= 5


def test_get_asset_is_case_insensitive(provider):
    upper = provider.get_asset("AAPL")
    lower = provider.get_asset("aapl")
    assert upper is not None
    assert upper == lower


def test_get_asset_unknown_symbol_returns_none(provider):
    assert provider.get_asset("NOTREAL") is None


def test_get_historical_prices_deterministic_across_calls(provider):
    start = date.today() - timedelta(days=30)
    end = date.today()
    first = provider.get_historical_prices("AAPL", start, end)
    second = provider.get_historical_prices("AAPL", start, end)
    assert [p.close for p in first] == [p.close for p in second]


def test_get_historical_prices_returns_correct_number_of_points(provider):
    start = date.today() - timedelta(days=10)
    end = date.today()
    points = provider.get_historical_prices("AAPL", start, end)
    assert len(points) == 11


def test_get_historical_prices_rejects_unknown_symbol(provider):
    with pytest.raises(ValueError):
        provider.get_historical_prices("NOTREAL", date.today() - timedelta(days=5), date.today())


def test_get_historical_prices_rejects_inverted_range(provider):
    with pytest.raises(ValueError):
        provider.get_historical_prices("AAPL", date.today(), date.today() - timedelta(days=5))


def test_get_historical_prices_all_positive(provider):
    start = date.today() - timedelta(days=60)
    end = date.today()
    points = provider.get_historical_prices("AAPL", start, end)
    assert all(p.close > 0 for p in points)


def test_get_options_chain_deterministic_across_calls(provider):
    first = provider.get_options_chain("SPY")
    second = provider.get_options_chain("SPY")
    assert [c.last for c in first.contracts] == [c.last for c in second.contracts]


def test_get_options_chain_contains_calls_and_puts(provider):
    chain = provider.get_options_chain("SPY")
    types = {c.option_type for c in chain.contracts}
    assert types == {"call", "put"}


def test_get_options_chain_prices_are_positive(provider):
    chain = provider.get_options_chain("SPY")
    assert all(c.bid >= 0 for c in chain.contracts)
    assert all(c.ask > 0 for c in chain.contracts)
    assert all(c.ask >= c.bid for c in chain.contracts)


def test_get_options_chain_implied_vols_are_positive(provider):
    chain = provider.get_options_chain("SPY")
    assert all(c.implied_volatility > 0 for c in chain.contracts)


def test_get_options_chain_unknown_symbol_raises(provider):
    with pytest.raises(ValueError):
        provider.get_options_chain("NOTREAL")


def test_get_option_contract_finds_matching_contract(provider):
    chain = provider.get_options_chain("AAPL")
    sample = chain.contracts[0]
    found = provider.get_option_contract(
        "AAPL", sample.strike, sample.expiry, sample.option_type
    )
    assert found is not None
    assert found.symbol == sample.symbol


def test_get_market_events_filters_by_symbol(provider):
    events = provider.get_market_events("AAPL")
    assert all(e.symbol == "AAPL" for e in events)
    assert len(events) > 0


def test_get_market_events_returns_all_when_no_symbol(provider):
    events = provider.get_market_events()
    symbols = {e.symbol for e in events}
    assert len(symbols) >= 5
