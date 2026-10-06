from typing import Tuple, List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models import User

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phoneNumber: str) -> Optional[User]:
    return db.query(User).filter(User.phoneNumber == phoneNumber).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(
    db: Session,
    filters: dict,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[User], int]:
    """Truy vấn danh sách người dùng có phân trang và bộ lọc"""
    query = db.query(User)

    if filters.get("roleID"):
        query = query.filter(User.roleID == filters["roleID"])

    if filters.get("status"):
        query = query.filter(User.status == filters["status"])

    if filters.get("search"):
        search_term = f"%{filters['search']}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.phoneNumber.ilike(search_term)
            )
        )

    query = query.order_by(User.id.desc())
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total

def update_user(db: Session, user_id: int, updated_fields: dict) -> Optional[User]:
    """Cập nhật thông tin người dùng theo ID"""
    user = get_user_by_id(db, user_id)
    if user:
        for key, value in updated_fields.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    """Xóa tài khoản người dùng"""
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user