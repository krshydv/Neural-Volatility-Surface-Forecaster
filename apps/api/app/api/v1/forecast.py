from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.forecasting.forecast_service import InsufficientHistoryError, run_volatility_forecast
from app.market_data.factory import get_market_data_provider
from app.market_data.provider import MarketDataProvider
from app.models.user import User
from app.schemas.forecast import (
    ForecastJobResponse,
    ForecastJobStatusResponse,
    ForecastPointResponse,
    VolatilityForecastRequest,
    VolatilityForecastResponse,
)

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.post("/{symbol}/volatility", response_model=VolatilityForecastResponse)
def forecast_volatility(
    symbol: str,
    payload: VolatilityForecastRequest,
    current_user: User = Depends(get_current_user),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    try:
        result = run_volatility_forecast(
            provider,
            symbol,
            horizon_days=payload.horizon_days,
            epochs=payload.epochs,
            model_type=payload.model_type,
        )
    except InsufficientHistoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return VolatilityForecastResponse(
        symbol=result.symbol,
        model_type=result.model_type,
        horizon_days=result.horizon_days,
        trained_on_observations=result.trained_on_observations,
        epochs=result.epochs,
        final_train_loss=result.final_train_loss,
        mean_absolute_error=result.mean_absolute_error,
        points=[
            ForecastPointResponse(
                forecast_date=p.forecast_date,
                volatility=p.volatility,
                lower_bound=p.lower_bound,
                upper_bound=p.upper_bound,
            )
            for p in result.points
        ],
    )


@router.post("/{symbol}/volatility/jobs", response_model=ForecastJobResponse, status_code=202)
def enqueue_forecast_volatility(
    symbol: str,
    payload: VolatilityForecastRequest,
    current_user: User = Depends(get_current_user),
):
    from app.workers.forecast_tasks import run_volatility_forecast_task

    try:
        task = run_volatility_forecast_task.delay(
            symbol,
            payload.horizon_days,
            payload.epochs,
            42,
            payload.model_type,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Training job queue unavailable — Celery broker (Redis) is unreachable",
        ) from exc

    return ForecastJobResponse(job_id=task.id, status="queued")


@router.get("/jobs/{job_id}", response_model=ForecastJobStatusResponse)
def get_forecast_job(job_id: str, current_user: User = Depends(get_current_user)):
    from app.workers.celery_app import celery_app

    result = celery_app.AsyncResult(job_id)
    payload = result.result if result.successful() else None
    error = str(result.result) if result.failed() else None

    return ForecastJobStatusResponse(
        job_id=job_id,
        status=result.status,
        result=payload,
        error=error,
    )
