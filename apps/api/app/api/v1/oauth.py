from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.auth import TokenPair
from app.schemas.oauth import OAuthAuthorizationUrlResponse, OAuthCallbackRequest
from app.services.auth_service import AuthService
from app.services.oauth_service import (
    GoogleOAuthService,
    OAuthConfigurationError,
    OAuthExchangeError,
)

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])


@router.get("/google/login", response_model=OAuthAuthorizationUrlResponse)
def google_login():
    settings = get_settings()
    service = GoogleOAuthService(settings)
    try:
        authorization_url, state = service.build_authorization_url()
    except OAuthConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return OAuthAuthorizationUrlResponse(authorization_url=authorization_url, state=state)


@router.post("/google/callback", response_model=TokenPair)
def google_callback(payload: OAuthCallbackRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    oauth_service = GoogleOAuthService(settings)
    try:
        userinfo = oauth_service.exchange_code_for_userinfo(payload.code)
    except OAuthConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except OAuthExchangeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    auth_service = AuthService(db)
    user = auth_service.login_or_register_oauth_user(
        userinfo["email"], userinfo.get("full_name")
    )
    return auth_service.issue_tokens(user)
