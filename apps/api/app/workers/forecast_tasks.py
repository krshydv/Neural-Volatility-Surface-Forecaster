from app.forecasting.forecast_service import run_volatility_forecast
from app.market_data.factory import get_market_data_provider
from app.workers.celery_app import celery_app


@celery_app.task(name="forecast.run_volatility_forecast", bind=True)
def run_volatility_forecast_task(
    self,
    symbol: str,
    horizon_days: int = 10,
    epochs: int = 400,
    seed: int = 42,
    model_type: str = "lstm",
):
    provider = get_market_data_provider()
    result = run_volatility_forecast(
        provider,
        symbol,
        horizon_days=horizon_days,
        epochs=epochs,
        seed=seed,
        model_type=model_type,
    )
    return {
        "symbol": result.symbol,
        "model_type": result.model_type,
        "horizon_days": result.horizon_days,
        "trained_on_observations": result.trained_on_observations,
        "epochs": result.epochs,
        "final_train_loss": result.final_train_loss,
        "mean_absolute_error": result.mean_absolute_error,
        "points": [
            {
                "forecast_date": p.forecast_date.isoformat(),
                "volatility": p.volatility,
                "lower_bound": p.lower_bound,
                "upper_bound": p.upper_bound,
            }
            for p in result.points
        ],
    }
