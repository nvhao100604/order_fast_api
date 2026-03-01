from realtime import Any, Union

from app.core.config import get_settings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.constants import TokenType

SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = get_settings().REFRESH_TOKEN_EXPIRE_DAYS
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CREATE TOKEN
def create_token(subject: Union[str, Any], expected_type: str = TokenType.ACCESS) -> str:
    now = datetime.now(timezone.utc)

    if expected_type == TokenType.ACCESS:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif expected_type == TokenType.REFRESH:
        expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError("Invalid token type")

    payload = {
        "sub": str(subject),
        "type": expected_type,
        "iat": now,     
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

# VERIFY TOKEN
def verify_token(token: str, expected_type: str = TokenType.ACCESS) -> dict:
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        
        if payload.get("type") != expected_type:
            return None
            
        return payload
        
    except JWTError:
        return None

# HASH PASSWORD
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# VERIFY PASSWORD
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)