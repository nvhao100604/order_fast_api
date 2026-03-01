
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import ResponseSchema, TokenResponse, Credential, UserResponse, UserCreate
from app.services import auth as auth_services 

router = APIRouter()

# LOGIN
@router.post(
    "/login",
    response_model=ResponseSchema[TokenResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Login",
    description="Authenticate user and return access and refresh tokens.",
)
async def login(response: Response, credential: Credential, db : Session = Depends(get_db)):
    response_data = auth_services.authenticate_user(credential=credential, db=db)
    auth_services.set_refresh_token_cookie(response=response, refresh_token=response_data.refresh_token)

    return ResponseSchema[TokenResponse](
        success=True,
        message="Login successful",
        data=response_data,
        meta=None
    )

# LOGOUT
@router.post(
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
@router.post(
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
@router.post(
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
@router.post(
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

