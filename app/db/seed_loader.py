import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Type, Callable

from app.db.session import SessionLocal
from app.db.base import Base
from app.models import (
    Role, Staff, Category, Dish, 
    Table, Customer, Order, OrderDetail, 
    Review, Discount
)
from app.models.customer import DiscountCategory
from app.models.ordering import TableStatus, OrderStatus

# =========================
# CẤU HÌNH ĐƯỜNG DẪN
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
SQL_FILE_PATH = BASE_DIR / "sql" / "mysql" / "website_order.sql"

# =========================
# REGEX XỬ LÝ SQL
# =========================
INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+[`\"]?(\w+)[`\"]?\s*\(([^)]+)\)\s*VALUES\s*(.*?)(?=;|\Z)",
    re.I | re.S,
)

# =========================
# BẢN ĐỒ CHUYỂN ĐỔI KIỂU DỮ LIỆU (Type Converters)
# =========================
# Giúp hàm Generic biết cách biến chuỗi từ SQL thành đối tượng Python chuẩn
TYPE_CONVERTERS: Dict[str, Callable] = {
    "id": int,
    "price": float,
    "totalPrice": float,
    "quantity": int,
    "rating": int,
    "status": lambda v: int(v) if v.isdigit() else v, 
    "categoryID": int,
    "roleID": int,
    "staffID": int,
    "customerID": int,
    "tableID": int,
    "dishID": int,
    "discountID": int,
    # Xử lý thời gian cho các bảng Order, Review, Discount
    "dateOrder": lambda v: datetime.fromisoformat(v.strip("'")),
    "category": lambda v: DiscountCategory(v.strip("'")),
    "dateBegin": lambda v: datetime.fromisoformat(v.strip("'")),
    "dateEnd": lambda v: datetime.fromisoformat(v.strip("'")),
    "created_at": lambda v: datetime.fromisoformat(v.strip("'")),
}

# =========================
# HÀM HỖ TRỢ BÓC TÁCH (Helpers)
# =========================
def _parse_insert_values(values_block: str) -> List[List[str]]:
    rows = []
    # Tìm các cụm (val1, val2, ...)
    for row in re.findall(r"\((.*?)\)", values_block, re.S):
        cols = []
        current = ""
        in_string = False
        for ch in row:
            if ch == "'" and not in_string: in_string = True
            elif ch == "'" and in_string: in_string = False
            
            if ch == "," and not in_string:
                cols.append(current.strip())
                current = ""
            else: current += ch
        if current: cols.append(current.strip())
        rows.append(cols)
    return rows

def _rows_to_dicts(columns: str, rows: List[List[str]]) -> List[Dict[str, str]]:
    col_names = [c.strip().strip("`").strip('"') for c in columns.split(",")]
    return [dict(zip(col_names, r)) for r in rows]

# =========================
# HÀM GENERIC DUY NHẤT (The Brain)
# =========================
def load_from_sql_generic(sql_content: str, table_name: str, model_class: Type) -> List[Any]:
    items = []
    for match in INSERT_RE.finditer(sql_content):
        if match.group(1).lower() != table_name.lower():
            continue

        records = _rows_to_dicts(match.group(2), _parse_insert_values(match.group(3)))
        model_columns = model_class.__table__.columns.keys()
        
        for r in records:
            processed_data = {}
            for key, val in r.items():
                if key in model_columns:
                    # Làm sạch chuỗi: xóa dấu nháy và khoảng trắng thừa
                    val_str = val.strip("'").strip() 
                    
                    # --- XỬ LÝ ENUM TẬP TRUNG ---
                    # 1. Xử lý cột 'status' cho bảng orders và tables
                    if key == "status":
                        if table_name == "orders":
                            processed_data[key] = OrderStatus(val_str)
                        elif table_name == "tables":
                            processed_data[key] = TableStatus(val_str)
                        else:
                            processed_data[key] = val_str
                            
                    # 2. Xử lý cột 'category' cho bảng discount
                    elif key == "category" and table_name == "discount":
                        # Ép kiểu từ 'order' (string) sang DiscountCategory.ORDER (Enum)
                        # Nếu DB lưu hoa (ORDER), dùng val_str.upper() nếu cần
                        try:
                            processed_data[key] = DiscountCategory(val_str)
                        except ValueError:
                            # Phòng trường hợp SQL là 'order' nhưng Enum định nghĩa là 'ORDER'
                            processed_data[key] = DiscountCategory(val_str.upper())
                    
                    # --- XỬ LÝ CÁC KIỂU DỮ LIỆU KHÁC ---
                    elif val_str.upper() == "NULL":
                        processed_data[key] = None
                    elif key in TYPE_CONVERTERS:
                        processed_data[key] = TYPE_CONVERTERS[key](val_str)
                    else:
                        processed_data[key] = val_str
            
            items.append(model_class(**processed_data))
    return items

# =========================
# HÀM THỰC THI CHÍNH (Main Execution)
# =========================
def run_seed():
    if not SQL_FILE_PATH.exists():
        print(f"❌ Không tìm thấy file: {SQL_FILE_PATH}")
        return

    db = SessionLocal()
    sql_content = SQL_FILE_PATH.read_text(encoding="utf-8")

    try:
        print("--- Đang dọn dẹp và nạp dữ liệu mới ---")
        # Thứ tự nạp cực kỳ quan trọng để không lỗi khóa ngoại (Foreign Key)
        # Bảng cha nạp trước, bảng con nạp sau
        table_order = [
            ("roles", Role),
            ("categories", Category),
            ("tables", Table),
            ("discount", Discount),
            ("customer", Customer),
            ("staff", Staff),
            ("dish", Dish),
            ("orders", Order),
            ("reviews", Review),
            ("order_detail", OrderDetail)
        ]

        for table_name, model_class in table_order:
            print(f"-> Đang nạp bảng: {table_name}...")
            # Xóa dữ liệu cũ (Tùy chọn, dùng CASCADE để sạch hoàn toàn)
            db.execute(re.compile(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE", re.I).pattern)
            
            # Nạp dữ liệu mới
            objects = load_from_sql_generic(sql_content, table_name, model_class)
            if objects:
                db.add_all(objects)
                db.commit()
                print(f"   ✅ Thành công: {len(objects)} bản ghi.")

        print("\n🏆 TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC NẠP THÀNH CÔNG!")

    except Exception as e:
        print(f"❌ LỖI HỆ THỐNG: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()