import random
import sys
from datetime import datetime, timezone

sys.path.insert(0, "/app")

from app.db.session import SessionLocal
from app.forecasting.forecast_service import run_volatility_forecast
from app.market_data.mock_provider import ASSET_REGISTRY, MockMarketDataProvider
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.auth_service import AuthService

DEMO_EMAIL = "demo@volaris.ai"
DEMO_PASSWORD = "VolarisDemo2026!"
DEMO_FULL_NAME = "Demo Analyst"
WORKSPACE_NAME = "Default Workspace"
DEMO_SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA", "META", "AMZN", "GOOGL", "SPY", "QQQ", "PLTR", "COIN", "JPM"]
MODEL_TYPES = ["lstm", "mlp"]
HORIZONS = [5, 10, 20]


def build_experiment_log(provider: MockMarketDataProvider) -> list[dict]:
    rng = random.Random(1337)
    entries = []
    for i in range(18):
        symbol = rng.choice(DEMO_SYMBOLS)
        model_type = rng.choice(MODEL_TYPES)
        horizon = rng.choice(HORIZONS)
        result = run_volatility_forecast(
            provider,
            symbol,
            horizon_days=horizon,
            epochs=150,
            seed=100 + i,
            model_type=model_type,
        )
        entries.append(
            {
                "symbol": result.symbol,
                "modelType": result.model_type,
                "horizonDays": result.horizon_days,
                "epochs": result.epochs,
                "meanAbsoluteError": result.mean_absolute_error,
                "finalTrainLoss": result.final_train_loss,
                "ranAt": datetime.now(timezone.utc).isoformat(),
            }
        )
    entries.reverse()
    return entries


def main() -> None:
    db = SessionLocal()
    try:
        users = UserRepository(db)
        workspaces = WorkspaceRepository(db)
        auth_service = AuthService(db)

        user = users.get_by_email(DEMO_EMAIL)
        if user is None:
            user = auth_service.register(DEMO_EMAIL, DEMO_PASSWORD, DEMO_FULL_NAME)
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print(f"Demo user already exists: {DEMO_EMAIL}")

        existing = [w for w in workspaces.list_for_owner(user.id) if w.name == WORKSPACE_NAME]
        workspace = existing[0] if existing else workspaces.create(
            user.id, WORKSPACE_NAME, "Seeded demo workspace with sample forecast runs"
        )

        provider = MockMarketDataProvider()
        experiment_log = build_experiment_log(provider)

        layout_state = {
            "selected_symbol": "NVDA",
            "surface_settings": {"method": "cubic", "gridResolution": 24},
            "experiment_log": experiment_log,
        }
        workspaces.update(workspace, layout_state=layout_state)

        print(f"Seeded workspace '{WORKSPACE_NAME}' with {len(experiment_log)} experiment log entries")
        print(f"Mock market data now includes {len(ASSET_REGISTRY)} assets: {', '.join(ASSET_REGISTRY.keys())}")
        print()
        print("Log in with:")
        print(f"  email:    {DEMO_EMAIL}")
        print(f"  password: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
