
from fastapi import APIRouter, Depends

from app.api import deps
from app.models.user import User
from app.schemas import UserResponse, ResponseSchema

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