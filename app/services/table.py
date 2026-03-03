from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import table as table_crud
from app.models.enum import OrderStatus

def get_tables(
    db: Session,
    filters: dict,
    page: int = 1,
    limit: int = 10,
):
    """Xử lý logic phân trang và lấy danh sách bàn"""
    if page < 1 or limit < 1:
        raise ValueError("Page and limit must be positive integers.")
        
    skip = (page - 1) * limit    
    return table_crud.get_tables(db, filters=filters, skip=skip, limit=limit)

def get_table(db: Session, table_id: int):
    """
    Truy vấn thông tin chi tiết của một bàn theo ID.
    Ném lỗi 404 nếu không tìm thấy bàn.
    """
    return table_crud.get_table(db, table_id)

def update_table_status(
    db: Session,
    table_id: int,
    table_status: str,
):
    """Cập nhật trạng thái bàn (Ví dụ: Chuyển từ FREE sang OCCUPIED)"""
    updated_table = table_crud.get_table(db=db, table_id=table_id)
    if not updated_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {table_id} not found"
        )
    return table_crud.update_table(db, table_id=table_id, obj_in={"status": table_status})
    
def update_table_info(
    db: Session,
    table_id: int,
    update_data: dict,
):
    """Cập nhật thông tin chung của bàn (số bàn, sức chứa...)"""
    updated_table = table_crud.get_table(db=db, table_id=table_id)
    if not updated_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {table_id} not found"
        )
    return table_crud.update_table(db, table_id=table_id, obj_in=update_data)

def delete_table(db: Session, table_id: int):
    """
    Service xử lý logic xóa bàn.
    Kiểm tra các ràng buộc trước khi thực hiện xóa khỏi DB.
    """
    table = table_crud.get_table(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )  

    active_orders = [
        order for order in table.orders 
        if order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING]
    ]

    if active_orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CANNOT_DELETE_ACTIVE_TABLE"
        )
    
    return table_crud.delete_table(db, table_id)