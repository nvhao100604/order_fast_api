from typing import Generator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.constants import RoleID
from app.core.security import verify_token
from app.db.session import SessionLocal

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.crud import user as user_crud
from app.models.enum import Status
from app.models.user import User
from app.schemas.token import TokenPayload

# Đường dẫn để Swagger UI biết chỗ lấy Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    payload = verify_token(token, expected_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The session is invalid or has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_data = TokenPayload(**payload)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token is in an invalid format."
        )
    user = user_crud.get_user_by_id(db, user_id=token_data.sub)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="The user does not exist in the system."
        )
    
    if user.status != Status.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your account is locked or not activated."
        )
        
    return user

class RoleChecker:
    def __init__(self, allowed_role_ids: list[int]):
        self.allowed_role_ids = allowed_role_ids

    def __call__(self, current_user: User = Depends(get_current_user)):
        # Kiểm tra xem User có roleID không và có nằm trong danh sách cho phép không
        if current_user.roleID not in self.allowed_role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập vào chức năng này."
            )
        return current_user

allow_admin = RoleChecker([RoleID.ADMIN])
allow_internal = RoleChecker([RoleID.ADMIN, RoleID.STAFF])
allow_customer = RoleChecker([RoleID.CUSTOMER])
allow_all = RoleChecker([RoleID.ADMIN, RoleID.STAFF, RoleID.CUSTOMER])

# def check_admin_role(
#     current_user = Depends(get_current_user)
# ):
#     if current_user.role != CredentialRole.STAFF:
#         raise HTTPException(status_code=403, detail="Only admin users are allowed to access this resource.")
#     return current_user

