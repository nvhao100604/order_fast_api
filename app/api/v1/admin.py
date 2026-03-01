
from fastapi import APIRouter, Depends

from app.api.deps import allow_admin


router = APIRouter(
    dependencies=[Depends(allow_admin)]
)

@router.post("/admin/users"
             
)
async def admin_create_user(data: UserCreate, db: Session = Depends(get_db)):
    # Admin có quyền chỉ định roleID (is_admin_creating=True)
    return auth_services.create_user_service(db, data, is_admin_creating=True)