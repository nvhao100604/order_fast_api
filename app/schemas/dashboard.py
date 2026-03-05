from typing import List

from app.schemas.base import BaseSchema

class TopDishResponse(BaseSchema):
    name: str
    count: int

    class Config:
        from_attributes = True

class DashboardDataResponse(BaseSchema):
    # Guests
    todayGuests: int
    todayReservations: int

    # Orders
    todayOrders: int
    pendingOrders: int
    monthlyOrders: int

    # Revenue
    todayRevenue: float  
    revenueGrowth: float
    monthlyRevenue: float

    # Tables
    availableTables: int
    occupiedTables: int
    RESERVEdTables: int

    # Top dishes
    topDishes: List[TopDishResponse]