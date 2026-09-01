import secrets
from urllib.parse import urlencode

import httpx

from app.core.config import Settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class OAuthConfigurationError(Exception):
    pass


class OAuthExchangeError(Exception):
    pass


class GoogleOAuthService:
    def __init__(self, settings: Settings) -> None:
        self.client_id = settings.google_oauth_client_id
        self.client_secret = settings.google_oauth_client_secret
        self.redirect_uri = settings.google_oauth_redirect_uri

    def _require_configured(self) -> None:
        if not self.client_id or not self.client_secret:
            raise OAuthConfigurationError(
                "Google OAuth is not configured — set GOOGLE_OAUTH_CLIENT_ID and "
                "GOOGLE_OAUTH_CLIENT_SECRET"
            )

    def build_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        self._require_configured()
        state = state or secrets.token_urlsafe(24)
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}", state

    def exchange_code_for_userinfo(self, code: str) -> dict:
        self._require_configured()
        token_response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        if token_response.status_code != 200:
            raise OAuthExchangeError("Failed to exchange authorization code with Google")

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise OAuthExchangeError("Google token response did not include an access token")

        userinfo_response = httpx.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if userinfo_response.status_code != 200:
            raise OAuthExchangeError("Failed to fetch user info from Google")

        payload = userinfo_response.json()
        if not payload.get("email"):
            raise OAuthExchangeError("Google user info did not include an email address")

        return {
            "email": payload["email"],
            "full_name": payload.get("name"),
            "provider_subject": payload.get("sub"),
        }
