from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import user as user_crud
from app.models.user import User
from app.schemas import UserResponse, UserUpdate, ResponseSchema

router = APIRouter()

@router.get(
    "/me",
    response_model=ResponseSchema[UserResponse],
    summary="Get Current User",
    description="Retrieve information about the currently authenticated user."
)
async def get_me(
    current_user: User = Depends(deps.get_current_user)
):
    return ResponseSchema[UserResponse](
        success=True,
        message="User information retrieved successfully",
        data=current_user
    )

@router.put(
    "/me",
    response_model=ResponseSchema[UserResponse],
    summary="Update Current User Profile",
    description="Update profile information for the currently authenticated user."
)
async def update_me(
    update_data: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    fields_dict = update_data.model_dump(exclude_none=True)

    # Nếu đổi email/sđt, kiểm tra trùng lặp với user khác
    if "email" in fields_dict and fields_dict["email"] != current_user.email:
        existing = user_crud.get_user_by_email(db, fields_dict["email"])
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use by another account."
            )

    if "phoneNumber" in fields_dict and fields_dict["phoneNumber"] != current_user.phoneNumber:
        existing = user_crud.get_user_by_phone(db, fields_dict["phoneNumber"])
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is already in use by another account."
            )

    updated_user = user_crud.update_user(db, user_id=current_user.id, updated_fields=fields_dict)

    return ResponseSchema[UserResponse](
        success=True,
        message="User profile updated successfully",
        data=updated_user
    )