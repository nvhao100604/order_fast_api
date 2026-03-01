from app.core.config import get_settings
from app.models.token import RefreshToken
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

days = get_settings().REFRESH_TOKEN_EXPIRE_DAYS

def create_refresh_token(db: Session, user_id: int, refresh_token: str, user_agent: str = None):
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    
    db_obj = RefreshToken(
        user_id=user_id,
        token=refresh_token,
        user_agent=user_agent,
        expires_at=expires_at
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def revoke_refresh_token(db: Session, token: str, user_id: int = None):
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    clean_expired_tokens(db, user_id=user_id)
    db.commit()

def revoke_all_user_tokens(db: Session, user_id: int):
    db.query(RefreshToken).filter(RefreshToken.userID == user_id).delete()
    clean_expired_tokens(db, user_id=user_id)
    db.commit()

def clean_expired_tokens(db: Session, user_id: int = None):
    db.query(RefreshToken).filter(
        RefreshToken.userID == user_id,
        RefreshToken.expiresAt < datetime.now(timezone.utc)
    ).delete()
    db.commit()