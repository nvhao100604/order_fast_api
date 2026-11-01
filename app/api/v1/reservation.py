from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status, Header, Response
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
from app.services.idempotency import compute_payload_hash, evaluate_idempotency, finalize_idempotency, fail_idempotency
from app.services.reservation_checkin import checkin_reservation

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
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db)
):
    if idempotency_key:
        payload_hash = compute_payload_hash(data.model_dump(mode="json"))
        cached, record = evaluate_idempotency(
            db=db,
            key=idempotency_key,
            user_id=None,
            path="/api/v1/reservations",
            payload_hash=payload_hash
        )
        if cached:
            response.headers["X-Cache-Lookup"] = "HIT"
            response.status_code = cached["code"]
            return cached["data"]

    try:
        new_reservation = reservation_service.create_reservation_service(
            db=db,
            data=data,
            current_user=None
        )
        res_payload = ResponseSchema[ReservationResponse](
            success=True,
            message="Reservation created successfully.",
            data=new_reservation
        )
        if idempotency_key:
            finalize_idempotency(
                db=db,
                key=idempotency_key,
                response_code=status.HTTP_201_CREATED,
                response_data=res_payload.model_dump(mode="json")
            )
            response.headers["X-Cache-Lookup"] = "MISS"
        return res_payload
    except Exception:
        if idempotency_key:
            fail_idempotency(db=db, key=idempotency_key)
        raise

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
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if idempotency_key:
        payload_hash = compute_payload_hash(data.model_dump(mode="json"))
        cached, record = evaluate_idempotency(
            db=db,
            key=idempotency_key,
            user_id=current_user.id,
            path="/api/v1/reservations/me",
            payload_hash=payload_hash
        )
        if cached:
            response.headers["X-Cache-Lookup"] = "HIT"
            response.status_code = cached["code"]
            return cached["data"]

    try:
        new_reservation = reservation_service.create_reservation_service(
            db=db,
            data=data,
            current_user=current_user
        )
        res_payload = ResponseSchema[ReservationResponse](
            success=True,
            message="Reservation created successfully.",
            data=new_reservation
        )
        if idempotency_key:
            finalize_idempotency(
                db=db,
                key=idempotency_key,
                response_code=status.HTTP_201_CREATED,
                response_data=res_payload.model_dump(mode="json")
            )
            response.headers["X-Cache-Lookup"] = "MISS"
        return res_payload
    except Exception:
        if idempotency_key:
            fail_idempotency(db=db, key=idempotency_key)
        raise

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

@private_router.post(
    "/{id}/checkin",
    summary="Check-in a reservation",
    description="Check-in a confirmed reservation, open linked tables, and create draft order."
)
async def checkin_reservation_endpoint(
    id: int = Path(..., ge=1, description="Reservation ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(allow_internal)
):
    result = checkin_reservation(db, reservation_id=id, staff_id=current_user.id)
    return ResponseSchema[dict](
        success=True,
        message=f"Reservation {id} checked in successfully.",
        data={
            "reservationID": result["reservation"].id,
            "orderID": result["order"].id if result["order"] else None,
            "tableIDs": [t.id for t in result["tables"]]
        }
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
