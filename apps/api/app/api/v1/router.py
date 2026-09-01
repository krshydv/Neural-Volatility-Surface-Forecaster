from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    assets,
    auth,
    forecast,
    health,
    oauth,
    options,
    quant,
    volatility,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(workspaces.router)
api_router.include_router(quant.router)
api_router.include_router(assets.router)
api_router.include_router(options.router)
api_router.include_router(volatility.router)
api_router.include_router(forecast.router)
api_router.include_router(analytics.router)
