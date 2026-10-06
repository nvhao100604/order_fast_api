from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import allow_admin, get_db
from app.crud import user as user_crud
from app.schemas import (
    UserCreate,
    UserResponse,
    UserAdminUpdate,
    UserFilter,
    ResponseSchema
)
from app.services import auth as auth_services

router = APIRouter(
    dependencies=[Depends(allow_admin)]
)

@router.get(
    "",
    response_model=ResponseSchema[List[UserResponse]],
    summary="Get List of Users (Admin)",
    description="Retrieve a paginated list of all users with search and filters."
)
async def get_users(
    filters: UserFilter = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    filter_dict = filters.model_dump(exclude_none=True)
    skip = (page - 1) * limit
    users, total = user_crud.get_users(db, filters=filter_dict, skip=skip, limit=limit)

    return ResponseSchema[List[UserResponse]](
        success=True,
        message="Get user list successfully.",
        data=users,
        meta={
            "page": page,
            "limit": limit,
            "total": total
        }
    )

@router.post(
    "",
    response_model=ResponseSchema[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create User by Admin",
    description="Admin creates a new user account with specified roleID and status."
)
async def admin_create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = auth_services.create_new_user(db=db, user_data=data, is_admin_creating=True)
    return ResponseSchema[UserResponse](
        success=True,
        message="User created successfully.",
        data=new_user
    )

@router.get(
    "/{id}",
    response_model=ResponseSchema[UserResponse],
    summary="Get User Details by ID",
    description="Retrieve detailed information about a specific user account."
)
async def get_user(
    id: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_id(db, user_id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    return ResponseSchema[UserResponse](
        success=True,
        message="Get user details successfully.",
        data=user
    )

@router.patch(
    "/{id}",
    response_model=ResponseSchema[UserResponse],
    summary="Update User Role / Status / Information",
    description="Update roleID, status, or profile fields for a user account."
)
@router.put(
    "/{id}",
    response_model=ResponseSchema[UserResponse],
    summary="Update User Role / Status / Information (PUT)",
    description="Update roleID, status, or profile fields for a user account."
)
async def update_user(
    update_data: UserAdminUpdate,
    id: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_id(db, user_id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    fields_dict = update_data.model_dump(exclude_none=True)
    updated_user = user_crud.update_user(db, user_id=id, updated_fields=fields_dict)

    return ResponseSchema[UserResponse](
        success=True,
        message="User updated successfully.",
        data=updated_user
    )

@router.patch(
    "/{id}/role",
    response_model=ResponseSchema[UserResponse],
    summary="Update User Role",
    description="Change roleID for a user account (e.g. 1: Admin, 2: Staff, 3: Customer)."
)
async def update_user_role(
    update_data: UserAdminUpdate,
    id: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db)
):
    return await update_user(update_data=update_data, id=id, db=db)

@router.patch(
    "/{id}/status",
    response_model=ResponseSchema[UserResponse],
    summary="Update User Account Status",
    description="Change status for a user account (e.g. active, inactive, banned)."
)
async def update_user_status(
    update_data: UserAdminUpdate,
    id: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db)
):
    return await update_user(update_data=update_data, id=id, db=db)


@router.delete(
    "/{id}",
    response_model=ResponseSchema[UserResponse],
    summary="Delete / Deactivate User Account",
    description="Delete a user account from the system."
)
async def delete_user(
    id: int = Path(..., ge=1, description="User ID"),
    db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_id(db, user_id=id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )

    deleted_user = user_crud.delete_user(db, user_id=id)
    return ResponseSchema[UserResponse](
        success=True,
        message="User deleted successfully.",
        data=deleted_user
    )