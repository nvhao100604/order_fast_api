from typing import Optional

from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class TokenResponseRefresh(TokenResponse):
    refresh_token: str

class Credential(BaseModel):
    username: str
    password: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    role: str
    type: str 