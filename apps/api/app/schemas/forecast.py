from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class VolatilityForecastRequest(BaseModel):
    horizon_days: int = Field(default=10, ge=1, le=30)
    epochs: int = Field(default=400, ge=50, le=2000)
    model_type: Literal["mlp", "lstm"] = "lstm"


class ForecastPointResponse(BaseModel):
    forecast_date: date
    volatility: float
    lower_bound: float
    upper_bound: float


class VolatilityForecastResponse(BaseModel):
    symbol: str
    model_type: str
    horizon_days: int
    trained_on_observations: int
    epochs: int
    final_train_loss: float
    mean_absolute_error: float
    points: list[ForecastPointResponse]


class ForecastJobResponse(BaseModel):
    job_id: str
    status: str


class ForecastJobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error: str | None = None
