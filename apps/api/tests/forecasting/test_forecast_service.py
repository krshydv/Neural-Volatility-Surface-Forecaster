import pytest

from app.forecasting.forecast_service import run_volatility_forecast
from app.market_data.mock_provider import MockMarketDataProvider


@pytest.fixture()
def provider():
    return MockMarketDataProvider()


def test_forecast_returns_requested_horizon(provider):
    result = run_volatility_forecast(provider, "AAPL", horizon_days=5, epochs=100)

    assert result.symbol == "AAPL"
    assert len(result.points) == 5
    assert result.trained_on_observations > 0


def test_forecast_volatility_is_positive(provider):
    result = run_volatility_forecast(provider, "SPY", horizon_days=8, epochs=100)

    for point in result.points:
        assert point.volatility > 0
        assert point.lower_bound <= point.volatility <= point.upper_bound


def test_forecast_bounds_widen_with_horizon(provider):
    result = run_volatility_forecast(provider, "NVDA", horizon_days=10, epochs=100)

    first_width = result.points[0].upper_bound - result.points[0].lower_bound
    last_width = result.points[-1].upper_bound - result.points[-1].lower_bound
    assert last_width >= first_width


def test_forecast_unknown_symbol_raises(provider):
    with pytest.raises(ValueError):
        run_volatility_forecast(provider, "NOTREAL", horizon_days=5, epochs=50)


def test_forecast_is_deterministic_for_same_seed(provider):
    first = run_volatility_forecast(provider, "QQQ", horizon_days=5, epochs=100, seed=7)
    second = run_volatility_forecast(provider, "QQQ", horizon_days=5, epochs=100, seed=7)

    assert [p.volatility for p in first.points] == [p.volatility for p in second.points]


def test_forecast_defaults_to_lstm(provider):
    result = run_volatility_forecast(provider, "AAPL", horizon_days=5, epochs=50)
    assert result.model_type == "lstm"


def test_forecast_supports_mlp_model_type(provider):
    result = run_volatility_forecast(
        provider, "AAPL", horizon_days=5, epochs=50, model_type="mlp"
    )
    assert result.model_type == "mlp"
    assert len(result.points) == 5


def test_forecast_lstm_volatility_is_positive(provider):
    result = run_volatility_forecast(
        provider, "TSLA", horizon_days=6, epochs=80, model_type="lstm"
    )
    for point in result.points:
        assert point.volatility > 0
        assert point.lower_bound <= point.volatility <= point.upper_bound


def test_forecast_rejects_unsupported_model_type(provider):
    with pytest.raises(ValueError):
        run_volatility_forecast(provider, "AAPL", horizon_days=5, epochs=50, model_type="rnn")
