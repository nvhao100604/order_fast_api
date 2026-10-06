from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, allow_all, allow_internal
from app.models.user import User
from app.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    ReservationFilter
)
from app.schemas.response import ResponseSchema
from app.services import reservation as reservation_service

public_router = APIRouter()
private_router = APIRouter()

# --- PUBLIC ENDPOINTS ---

@public_router.post(
    "",
    response_model=ResponseSchema[ReservationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation",
    description="Public endpoint to submit a table reservation request."
)
async def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db)
):
    new_reservation = reservation_service.create_reservation_service(
        db=db,
        data=data,
        current_user=None
    )
    return ResponseSchema[ReservationResponse](
        success=True,
        message="Reservation created successfully.",
        data=new_reservation
    )

# --- PRIVATE ENDPOINTS ---

@private_router.post(
    "/me",
    response_model=ResponseSchema[ReservationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a reservation for authenticated user",
    description="Create a table reservation tied to the current logged-in user."
)
async def create_my_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_reservation = reservation_service.create_reservation_service(
        db=db,
        data=data,
        current_user=current_user
    )
    return ResponseSchema[ReservationResponse](
        success=True,
        message="Reservation created successfully.",
        data=new_reservation
    )

@private_router.get(
    "",
    response_model=ResponseSchema[List[ReservationResponse]],
    summary="Get list of reservations",
    description="Retrieve a paginated list of reservations with filters."
)
async def get_reservations(
    filters: ReservationFilter = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filter_dict = filters.model_dump(exclude_none=True)
    reservations, total = reservation_service.get_reservations_service(
        db=db,
        filters=filter_dict,
        page=page,
        limit=limit,
        current_user=current_user
    )
    return ResponseSchema[List[ReservationResponse]](
        success=True,
        message="Get reservation list successfully.",
        data=reservations,
        meta={
            "page": page,
            "limit": limit,
            "total": total
        }
    )

@private_router.get(
    "/{id}",
    response_model=ResponseSchema[ReservationResponse],
    summary="Get reservation details by ID",
    description="Retrieve detailed information about a specific reservation."
)
async def get_reservation_detail(
    id: int = Path(..., ge=1, description="Reservation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reservation = reservation_service.get_reservation_detail_service(
        db=db,
        reservation_id=id,
        current_user=current_user
    )
    return ResponseSchema[ReservationResponse](
        success=True,
        message="Get reservation details successfully.",
        data=reservation
    )

@private_router.patch(
    "/{id}",
    response_model=ResponseSchema[ReservationResponse],
    summary="Update reservation info / status / table assignment",
    description="Update reservation details, status, or assign table (Staff/Admin/User)."
)
async def update_reservation(
    update_data: ReservationUpdate,
    id: int = Path(..., ge=1, description="Reservation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated = reservation_service.update_reservation_service(
        db=db,
        reservation_id=id,
        update_data=update_data,
        current_user=current_user
    )
    return ResponseSchema[ReservationResponse](
        success=True,
        message="Update reservation successfully.",
        data=updated
    )

@private_router.post(
    "/{id}/cancel",
    response_model=ResponseSchema[ReservationResponse],
    summary="Cancel a reservation",
    description="Cancel a reservation and release table if assigned."
)
async def cancel_reservation(
    id: int = Path(..., ge=1, description="Reservation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cancelled = reservation_service.cancel_reservation_service(
        db=db,
        reservation_id=id,
        current_user=current_user
    )
    return ResponseSchema[ReservationResponse](
        success=True,
        message="Reservation cancelled successfully.",
        data=cancelled
    )

@private_router.delete(
    "/{id}",
    response_model=ResponseSchema[ReservationResponse],
    summary="Delete reservation (Admin only)",
    dependencies=[Depends(allow_internal)],
    description="Permanently delete a reservation from the database."
)
async def delete_reservation(
    id: int = Path(..., ge=1, description="Reservation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = reservation_service.delete_reservation_service(
        db=db,
        reservation_id=id
    )
    return ResponseSchema[ReservationResponse](
        success=True,
        message="Reservation deleted successfully.",
        data=deleted
    )
