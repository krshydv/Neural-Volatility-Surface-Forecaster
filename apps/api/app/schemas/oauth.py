from pydantic import BaseModel


class OAuthAuthorizationUrlResponse(BaseModel):
    authorization_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str | None = None
