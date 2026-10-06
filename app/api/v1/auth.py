from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas import (
    ResponseSchema,
    TokenResponse,
    Credential,
    UserResponse,
    UserCreate,
    SendOTPRequest,
    VerifyOTPRequest,
    ResetPasswordRequest
)
from app.services import auth as auth_services 

public_router = APIRouter()
private_router = APIRouter()

# LOGIN
@public_router.post(
    "/login",
    response_model=TokenResponse,
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Login",
    description="Authenticate user and return access and refresh tokens.",
)
async def login(
    request: Request, 
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)):

    tokens = auth_services.authenticate_user(
        db=db, 
        request=request, 
        username=form_data.username, 
        password=form_data.password
    )

    auth_services.set_refresh_token_cookie(response=response, refresh_token=tokens.refresh_token)

    return tokens

# LOGOUT
@private_router.post(
    "/logout",
    response_model=ResponseSchema,
    summary="Logout",
    description="Revoke refresh token and clear authentication cookies."
)
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token_from_cookie = request.cookies.get("refresh_token")
    if token_from_cookie:
        auth_services.revoke_refresh_token(db=db, token=token_from_cookie)

    auth_services.delete_refresh_token_cookie(response=response)

    return ResponseSchema(
        success=True,
        message="Logged out successfully",
        data=None
    )

# REFRESH TOKEN
@public_router.post(
    "/refresh-token",
    response_model=ResponseSchema[TokenResponse],
    summary="Refresh Token",
    description="Get a new access token using the refresh token from cookies."
)
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    token_from_cookie = request.cookies.get("refresh_token")
    
    if not token_from_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    new_token_data = auth_services.refresh_access_token(db=db, refresh_token=token_from_cookie)

    return ResponseSchema[TokenResponse](
        success=True,
        message="Token refreshed successfully",
        data=new_token_data
    )

# REGISTER
@public_router.post(
    "/register",
    response_model=ResponseSchema[UserResponse],
    summary="Register",
    description="Register a new customer account."
)
async def register(data: UserCreate, db: Session = Depends(get_db)):    
    new_user = auth_services.create_new_user(db=db, user_data=data)
    
    return ResponseSchema[UserResponse](
        success=True,
        message="Registration successful",
        data=new_user
    )

# REVOKE ALL TOKENS
@private_router.post(
    "/revoke-all-tokens",
    response_model=ResponseSchema,
    summary="Revoke All Tokens",
    description="Revoke all refresh tokens for the authenticated user."
)
async def revoke_all_tokens(request: Request, db: Session = Depends(get_db)):
    token_from_cookie = request.cookies.get("refresh_token")
    if not token_from_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    auth_services.revoke_all_user_tokens(db=db, token=token_from_cookie)

    return ResponseSchema(
        success=True,
        message="All tokens revoked successfully",
        data=None
    )

# FORGOT PASSWORD - STEP 1: SEND OTP
@public_router.post(
    "/forgot-password/send-otp",
    response_model=ResponseSchema,
    summary="Forgot Password - Send OTP",
    description="Send a password reset OTP code to user email."
)
async def send_forgot_password_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    otp_code = auth_services.send_forgot_password_otp(db=db, email=data.email)
    return ResponseSchema(
        success=True,
        message="OTP code sent to email.",
        data={"email": data.email, "dev_otp": otp_code}
    )

# FORGOT PASSWORD - STEP 2: VERIFY OTP
@public_router.post(
    "/forgot-password/verify-otp",
    response_model=ResponseSchema,
    summary="Forgot Password - Verify OTP",
    description="Verify the received OTP code."
)
async def verify_forgot_password_otp(data: VerifyOTPRequest):
    auth_services.verify_forgot_password_otp(email=data.email, otp=data.otp)
    return ResponseSchema(
        success=True,
        message="OTP verified successfully.",
        data=None
    )

# FORGOT PASSWORD - STEP 3: RESET PASSWORD
@public_router.post(
    "/forgot-password/reset-password",
    response_model=ResponseSchema,
    summary="Forgot Password - Reset Password",
    description="Reset user password using verified OTP."
)
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_services.reset_password_with_otp(
        db=db,
        email=data.email,
        otp=data.otp,
        new_password=data.newPassword
    )
    return ResponseSchema(
        success=True,
        message="Password reset successfully.",
        data=None
    )
