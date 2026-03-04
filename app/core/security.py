import hashlib

import bcrypt
from realtime import Any, Union

from app.core.config import get_settings
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.core.constants import TokenType

SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_EXPIRE_DAYS = get_settings().REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

# CREATE TOKEN
def create_token(subject: Union[str, Any], 
    roleId: int,  
    expires_delta: int,           
    expected_type: str = TokenType.ACCESS,
) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(seconds=expires_delta)
    payload = {
        "sub": str(subject),
        "roleId": roleId,
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
    prepared_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prepared_password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')

# VERIFY PASSWORD
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        prepared_password = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return bcrypt.checkpw(
            prepared_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False