from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.deps import get_current_user_ws
from app.api.v1 import router
from app.core.config import settings
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import global_exception_handler, http_exception_handler, validation_exception_handler, value_error_handler
from app.core.websocket import manager
from app.models.user import User

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An backend API for order management",
    version="1.0.0",
    )

# Thêm vào sau phần khởi tạo app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://order-front-end-2.vercel.app", 
        "https://order-front-end-blond.vercel.app",
        "https://order-vh.vercel.app",
        "http://localhost:3000"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', include_in_schema=False) #
def read_root():
    return RedirectResponse(url="/docs")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket,
                             current_user: User = Depends(get_current_user_ws)):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.include_router(router.api_router, prefix="/api/v1") 