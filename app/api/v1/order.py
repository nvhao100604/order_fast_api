from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.constants import RoleID
from app.models.user import User
from app.schemas.ordering import OrderCreate, OrderFilter, OrderResponse
from app.schemas.response import ResponseSchema
from app.services import order as order_service
from app.api.deps import allow_all

router = APIRouter(
    dependencies=[Depends(allow_all)]
)

@router.get(
    "",
    response_model=ResponseSchema[List[OrderResponse]],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model" : ResponseSchema}},
    summary="Get orders with pagination",
    description="Get a paginated list of orders from the database."
)
async def get_orders(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    filters: OrderFilter = Depends(),
    current_user: User = Depends(get_current_user)
):
    filters_dict = filters.model_dump(exclude={"staffID", "customerID"})

    if current_user.roleID == RoleID.CUSTOMER:
        filters_dict["customerId"] = current_user.id

    elif current_user.roleID == RoleID.STAFF:
        filters_dict["customer_id"] = filters.customerID
        if filters.staffID:
            filters_dict["staff_id"] = filters.staffID

    elif current_user.roleID == RoleID.ADMIN:
        filters_dict["customer_id"] = filters.customerID
        filters_dict["staff_id"] = filters.staffID
    
    orders, total = order_service.get_orders(
        db=db, 
        page=page, 
        limit=limit, 
        filters=filters_dict, 
        current_user=current_user)

    return ResponseSchema[List[OrderResponse]](
        data=orders,
        message="Get order list successfully.",
        meta={
            "page": page,
            "limit": limit,
            "total": total
        }
    )

@router.post(
    "",
    response_model=ResponseSchema[OrderResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema} },
    summary="Create an order",
    description="Create an order and insert to the database."
)
async def post_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order_dict = order_data.model_dump()

    if current_user.roleID == RoleID.CUSTOMER:
        # Nếu là khách: Ghi đè customerID bằng ID của chính họ để tránh đặt hộ người khác
        order_dict["customerID"] = current_user.id
    else:
        # Nếu là Staff/Admin: Lấy customerID từ data gửi lên (để tạo đơn hộ khách)
        if not order_dict.get("customerID"):
            raise HTTPException(status_code=400, detail="This action need the customerID.")

    new_order = order_service.post_order(db=db, order_in=order_dict)
    
    return ResponseSchema[OrderResponse](
        message="Create the order successfully.",
        data=new_order
    )

@router.get(
    "/{id}",
    response_model=ResponseSchema[OrderResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Get an order by id.",
    description="Get an order's information by order id."
)
async def get_order(
    id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = order_service.get_order(db=db, id=id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Nếu KHÔNG PHẢI Admin/Staff (1, 2) VÀ userID của đơn không khớp với người đang gọi
    if current_user.roleID not in [RoleID.ADMIN, RoleID.STAFF] and order.customerID != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Do not have permission to view this order information."
        )

    return ResponseSchema[OrderResponse](
        data=order,
        message="Get order's information successfully."
    )