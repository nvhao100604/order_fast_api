from typing import List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ordering import OrderCreate, OrderFilter, OrderResponse
from app.schemas.response import ResponseSchema
from app.services import order as order_service

router = APIRouter()

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
    filters: OrderFilter = Depends()
):
    filters_dict = filters.model_dump(exclude_none=True)
    orders, total = order_service.get_orders(db=db, page=page, limit=limit, filters=filters_dict)

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
    order: OrderCreate,
    db: Session = Depends(get_db),
):
    order = order_service.post_order(db=db, order=order)
    return ResponseSchema[OrderResponse](
        message="Create the order successfully.",
        data=order
    )

@router.get(
    "/{id}",
    response_model=ResponseSchema[OrderResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Get an order by id.",
    description="Get an order's information by order id."
)
async def get_order(
    db: Session = Depends(get_db),
    id: int = Path(..., description="ID of the order", ge=1)
):
    order = order_service.get_order(db=db, id=id)
    return ResponseSchema[OrderResponse](
        data=order,
        message="Get order's information successfully."
    )