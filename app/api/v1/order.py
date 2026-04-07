from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.constants import RoleID
from app.models.enum import OrderStatus
from app.models.user import User
from app.schemas.ordering import OrderCreate, OrderFilter, OrderResponse
from app.schemas.response import ResponseSchema
from app.services import order as order_service
from app.api.deps import allow_all
from app.core.websocket import manager

router = APIRouter(
    dependencies=[Depends(allow_all)]
)

@router.get(
    "",
    response_model=ResponseSchema[List[OrderResponse]],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Get orders with pagination",
    description="Get a paginated list of orders from the database."
)
async def get_orders(
    db: Session = Depends(get_db),
    page: int = Query(1),
    limit: int = Query(10),
    filters: OrderFilter = Depends(),
    current_user: User = Depends(get_current_user)
):
    orders, total = order_service.get_orders(
        db=db,
        page=page,
        limit=limit,
        filters=filters,          
        current_user=current_user
    )

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
    if current_user.roleID == RoleID.CUSTOMER:
        # Nếu là khách: Ghi đè customerID bằng ID của chính họ để tránh đặt hộ người khác
        order_data.customerID = current_user.id
        order_data.staffID = 1
    else:
        # Nếu là Staff/Admin: Lấy customerID từ data gửi lên (để tạo đơn hộ khách)
        if not order_data.customerID:
            raise HTTPException(status_code=400, detail="This action need the customerID.")

    new_order = order_service.post_order(db=db, order_in=order_data)

    await manager.broadcast({
        "type": "NEW_ORDER",
        "order_id": new_order.id,
        "customer_name": current_user.name,
        "message": f"Have new order from {new_order.tableID}!"
    })

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

@router.patch(
    "/{id}/status",
    response_model=ResponseSchema[OrderResponse],
    summary="Update Order Status",
    description="Update the status of an existing order. Valid statuses include: PENDING, CONFIRMED, PREPARING, SHIPPING, COMPLETED, CANCELLED, UNPAID."
)
async def patch_order_status(
    id: int = Path(..., ge=1, description="The ID of the order to update"),
    new_status: OrderStatus = Query(..., description="The new status to set for the order"),
    db: Session = Depends(get_db),
    current_staff: User = Depends(get_current_user)
):
    """
    Endpoint cập nhật trạng thái đơn hàng.
    Service sẽ tự động ném lỗi 404 nếu không tìm thấy đơn hàng.
    """
    print(f"status: {new_status}")
    updated_order = order_service.update_order_status(
        db=db, 
        order_id=id, 
        new_status=new_status,
        current_staff=current_staff
    )
    
    await manager.broadcast({
        "type": "STATUS_UPDATED",
        "order_id": id,
        "new_status": new_status.value,
        "message": f"Order with id: #{id} turned to new status: {new_status.value}"
    })

    return ResponseSchema[OrderResponse](
        data=updated_order,
        message=f"Order status updated to {new_status.value} successfully."
    )