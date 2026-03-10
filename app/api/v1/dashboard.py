from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas import ResponseSchema, OrderResponse, TableResponse
from app.services import dashboard as dash_services
# Giả sử bạn có dependency để check token cho private router
from app.api.deps import get_current_user, allow_internal

public_router = APIRouter()
private_router = APIRouter(
    dependencies=[Depends(allow_internal)]
    )

# --- PUBLIC ENDPOINTS ---

@public_router.get(
    "/tables",
    response_model=ResponseSchema[List[TableResponse]],
    summary="Get all tables",
    description="Retrieve a list of all tables in the restaurant. This is a public endpoint."
)
async def get_tables(db: Session = Depends(get_db)):
    tables = dash_services.get_all_tables(db)
    
    return ResponseSchema[List[TableResponse]](
        success=True,
        message="Tables retrieved successfully",
        data=tables
    )


# --- PRIVATE ENDPOINTS ---

@private_router.get(
    "/orders",
    response_model=ResponseSchema[List[OrderResponse]],
    summary="Get all orders",
    description="Retrieve all orders for the dashboard. Requires authentication.",
    dependencies=[Depends(get_current_user)] 
)
async def get_orders(db: Session = Depends(get_db)):
    orders = dash_services.get_all_orders(db)
    
    return ResponseSchema[List[OrderResponse]](
        success=True,
        message="Orders retrieved successfully",
        data=orders
    )