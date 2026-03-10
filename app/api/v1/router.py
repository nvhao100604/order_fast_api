from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.v1 import auth, dashboard, dish, category, order, table, user

api_router = APIRouter()

secure_router = APIRouter(dependencies=[Depends(get_current_user)])
secure_router.include_router(auth.private_router, prefix="/auth", tags=["Auth"])
secure_router.include_router(dish.private_router, prefix="/dishes", tags=["Dish"])
secure_router.include_router(order.router, prefix="/orders", tags=["Order"])
secure_router.include_router(user.router, prefix="/users", tags=["User"])
secure_router.include_router(table.private_router, prefix="/tables", tags=["Table"])
secure_router.include_router(dashboard.private_router, prefix="/dashboard", tags=["Dashboard"])


public_router = APIRouter()
public_router.include_router(auth.public_router, prefix="/auth", tags=["Auth"])
public_router.include_router(dish.public_router, prefix="/dishes", tags=["Dish"])
public_router.include_router(category.router, prefix="/categories", tags=["Category"])
public_router.include_router(table.public_router, prefix="/tables", tags=["Table"])
public_router.include_router(dashboard.public_router, prefix="/dashboard", tags=["Dashboard"])



api_router.include_router(secure_router)
api_router.include_router(public_router)

