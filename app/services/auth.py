from fastapi import HTTPException, Response, status
from httpx import request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, create_token, create_token, get_password_hash, verify_password, verify_token
from app.crud import user as user_crud
from app.crud import token as token_crud
from app.models.user import User
from app.schemas.token import Credential, TokenResponseRefresh
from app.schemas.user import UserCreate

# AUTHENTICATE USER
def authenticate_user(credential: Credential, db: Session) -> TokenResponseRefresh:
    # 1. Kiểm tra xem user có tồn tại không
    user = user_crud.get_user_by_username(db, credential.username) 
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # 2. Kiểm tra mật khẩu
    if not verify_password(credential.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # 3. Tạo access token và refresh token
    access_token = create_token(
        subject=user.id, 
        roleId=user.roleID,
        expected_type="access", 
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    refresh_token = create_token(
        subject=user.id, 
        roleId=user.roleID,
        expected_type="refresh", 
        expires_delta=REFRESH_TOKEN_EXPIRE_DAYS)
    
    user_agent = request.headers.get("User-Agent", "unknown")

    token_crud.create_refresh_token(
        db, 
        user_id=user.id, 
        refresh_token=refresh_token,
        user_agent=user_agent 
    )
    return TokenResponseRefresh(access_token=access_token, refresh_token=refresh_token)

# REFRESH ACCESS TOKEN
def refresh_access_token(refresh_token: str, db: Session) -> TokenResponseRefresh:
    # 1. Verify refresh token
    payload = verify_token(refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    # 2. Kiểm tra xem user có tồn tại không
    user = user_crud.get_user_by_username(db, username=user_id) 
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # 3. Tạo mới access token
    new_access_token = create_token(
        subject=user.id, 
        expected_type="access", 
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return TokenResponseRefresh(access_token=new_access_token, refresh_token=refresh_token)

# SET REFRESH TOKEN COOKIE
def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,   
        secure=True,   
        samesite="lax",  
        max_age=get_settings().REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/",
    )

# CREATE NEW USER
def create_new_user(db: Session, user_data: UserCreate, is_admin_creating: bool = False):
    # 1. Kiểm tra Username
    if user_crud.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tên đăng nhập này đã tồn tại"
        )
    
    # 2. Kiểm tra Email
    if user_crud.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email này đã được sử dụng"
        )
        
    # 3. Kiểm tra Số điện thoại
    if user_crud.get_user_by_phone(db, user_data.phoneNumber):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Số điện thoại này đã được sử dụng"
        )
    
    # 4. Băm mật khẩu (Security)
    hashed_password = get_password_hash(user_data.password)
    
    user_dict = user_data.model_dump(exclude={"password"})
    
    # 5. CHỐT CHẶN BẢO MẬT:
    if not is_admin_creating:
        # Nếu là khách tự đăng ký qua /register, luôn ép roleID = 3
        user_dict["roleID"] = 3 
    elif user_dict.get("roleID") is None:
        # Nếu Admin tạo mà quên gửi roleID, mặc định gán là Staff (ID = 2)
        user_dict["roleID"] = 2

    # 6. Khởi tạo Model và lưu
    new_user = User(**user_dict, password=hashed_password)
    return user_crud.create_user(db, new_user)


# DELETE REFRESH TOKEN COOKIE
def delete_refresh_token_cookie(response: Response):
    response.delete_cookie(key="refresh_token", path="/")

# REVOKE REFRESH TOKEN
def revoke_refresh_token(db: Session, token: str):
    payload = verify_token(token, expected_type="refresh")
    if not payload:
        return  # Token không hợp lệ, không cần thu hồi
    
    user_id = payload.get("sub")
    if user_id:
        token_crud.revoke_refresh_token(db, token=token, user_id=user_id)

# REVOKE ALL USER TOKENS
def revoke_all_user_tokens(db: Session, token: str):
    payload = verify_token(token, expected_type="refresh")
    if not payload:
        return  # Token không hợp lệ, không cần thu hồi
    
    user_id = payload.get("sub")
    if user_id:
        token_crud.revoke_all_user_tokens(db, token=token, user_id=user_id)
    