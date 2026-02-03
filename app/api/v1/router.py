from fastapi import APIRouter
from app.api.v1 import dish, category

api_router = APIRouter()

api_router.include_router(dish.router, prefix="/dishes", tags=["Dish"])
api_router.include_router(category.router, prefix="/categories", tags=["Category"])