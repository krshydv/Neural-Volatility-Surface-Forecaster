from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from app.forecasting.features import LOOKBACK_WINDOWS, build_dataset
from app.forecasting.lstm import LSTMRegressor
from app.forecasting.neural_net import MLPRegressor
from app.market_data.provider import MarketDataProvider

HISTORY_DAYS = 420
DEFAULT_EPOCHS = 400
DEFAULT_SEED = 42
DEFAULT_MODEL_TYPE = "lstm"
SUPPORTED_MODEL_TYPES = ("mlp", "lstm")


@dataclass(frozen=True)
class ForecastPoint:
    forecast_date: date
    volatility: float
    lower_bound: float
    upper_bound: float


@dataclass(frozen=True)
class ForecastResult:
    symbol: str
    model_type: str
    horizon_days: int
    trained_on_observations: int
    epochs: int
    final_train_loss: float
    mean_absolute_error: float
    points: list[ForecastPoint]


class InsufficientHistoryError(ValueError):
    pass


class UnsupportedModelTypeError(ValueError):
    pass


def _build_model(model_type: str, seed: int):
    if model_type == "mlp":
        return MLPRegressor(input_dim=LOOKBACK_WINDOWS, seed=seed)
    if model_type == "lstm":
        return LSTMRegressor(timesteps=LOOKBACK_WINDOWS, seed=seed)
    raise UnsupportedModelTypeError(
        f"Unsupported model_type '{model_type}'. Supported: {SUPPORTED_MODEL_TYPES}"
    )


def run_volatility_forecast(
    provider: MarketDataProvider,
    symbol: str,
    horizon_days: int = 10,
    epochs: int = DEFAULT_EPOCHS,
    seed: int = DEFAULT_SEED,
    model_type: str = DEFAULT_MODEL_TYPE,
) -> ForecastResult:
    if provider.get_asset(symbol) is None:
        raise ValueError(f"Unknown symbol: {symbol}")

    model_type = model_type.lower()
    end = date.today()
    start = end - timedelta(days=HISTORY_DAYS)
    prices = provider.get_historical_prices(symbol, start, end)

    try:
        dataset = build_dataset(prices)
    except ValueError as exc:
        raise InsufficientHistoryError(str(exc)) from exc

    model = _build_model(model_type, seed)
    loss_history = model.train(dataset.x, dataset.y, epochs=epochs)

    train_predictions = model.predict(dataset.x) * dataset.target_std + dataset.target_mean
    train_actual = dataset.y * dataset.target_std + dataset.target_mean
    mae = float(np.mean(np.abs(train_predictions - train_actual)))

    window = dataset.latest_window.copy()
    points: list[ForecastPoint] = []
    horizon_dates = _future_business_days(end, horizon_days)

    for i, forecast_date in enumerate(horizon_dates):
        normalized_window = (window - dataset.feature_mean) / dataset.feature_std
        prediction = model.predict(normalized_window.reshape(1, -1))[0]
        volatility = float(prediction * dataset.target_std + dataset.target_mean)
        volatility = max(volatility, 0.01)

        band = mae * (1.0 + 0.15 * i)
        points.append(
            ForecastPoint(
                forecast_date=forecast_date,
                volatility=volatility,
                lower_bound=max(volatility - band, 0.0),
                upper_bound=volatility + band,
            )
        )

        window = np.roll(window, -1)
        window[-1] = volatility

    return ForecastResult(
        symbol=symbol.upper(),
        model_type=model_type,
        horizon_days=horizon_days,
        trained_on_observations=dataset.x.shape[0],
        epochs=epochs,
        final_train_loss=float(loss_history[-1]),
        mean_absolute_error=mae,
        points=points,
    )


def _future_business_days(start: date, count: int) -> list[date]:
    days: list[date] = []
    cursor = start
    while len(days) < count:
        cursor = cursor + timedelta(days=1)
        if cursor.weekday() < 5:
            days.append(cursor)
    return days
