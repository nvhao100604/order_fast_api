from fastapi import FastAPI
from app.api.v1 import router
from app.core.config import settings
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import global_exception_handler, validation_exception_handler, value_error_handler

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An backend API for order management",
    version="1.0.0",
    )

# @app.get('/') #
# def read_root():
#     return RedirectResponse(url="/docs")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(router.api_router, prefix="/api/v1") 