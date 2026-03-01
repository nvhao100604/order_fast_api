from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.v1 import auth, dish, category, order, users

api_router = APIRouter()

secure_router = APIRouter(dependencies=[Depends(get_current_user)])
secure_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
secure_router.include_router(order.router, prefix="/orders", tags=["Order"])
secure_router.include_router(users.router, prefix="/users", tags=["User"])


public_router = APIRouter()
api_router.include_router(dish.router, prefix="/dishes", tags=["Dish"])
api_router.include_router(category.router, prefix="/categories", tags=["Category"])

api_router.include_router(secure_router)
api_router.include_router(public_router)

