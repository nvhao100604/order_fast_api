from app.core.config import get_settings
from app.models.token import RefreshToken
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

days = get_settings().REFRESH_TOKEN_EXPIRE_DAYS

def create_refresh_token(db: Session, userId: int, refresh_token: str, userAgent: str = None):
    expiresAt = datetime.now(timezone.utc) + timedelta(days=days)
    
    db_obj = RefreshToken(
        userId=userId,
        token=refresh_token,
        userAgent=userAgent,
        expiresAt=expiresAt
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def revoke_refresh_token(db: Session, token: str, userId: int = None):
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    clean_expired_tokens(db, userId=userId)
    db.commit()

def revoke_all_user_tokens(db: Session, userId: int):
    db.query(RefreshToken).filter(RefreshToken.userId == userId).delete()
    clean_expired_tokens(db, userId=userId)
    db.commit()

def clean_expired_tokens(db: Session, userId: int = None):
    db.query(RefreshToken).filter(
        RefreshToken.userId == userId,
        RefreshToken.expiresAt < datetime.now(timezone.utc)
    ).delete()
    db.commit()