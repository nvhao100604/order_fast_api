from fastapi import FastAPI
from app.api.v1 import router
from app.core.config import settings
from fastapi.responses import RedirectResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An backend API for order management",
    version="1.0.0",
    )

# @app.get('/') #
# def read_root():
#     return RedirectResponse(url="/docs")

app.include_router(router.api_router, prefix="/api/v1") 