import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Type, Callable

from app.db.session import SessionLocal
from app.db.base import Base
from app.models import (
    Role, User, Category, Dish, 
    Table, Order, OrderDetail, 
    Review, Discount
)
from app.models.enum import DiscountCategory, TableStatus, OrderStatus


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
    # Lookup dictionaries for column and attribute names
    attr_by_name = {}
    if hasattr(model_class, "__mapper__"):
        for attr in model_class.__mapper__.column_attrs:
            attr_by_name[attr.key] = attr.key
            for col in attr.columns:
                attr_by_name[col.name] = attr.key

    # Legacy SQL column aliases for specific tables
    if table_name == "reviews":
        attr_by_name["customerID"] = "userID"
        attr_by_name["customer_id"] = "userID"

    for match in INSERT_RE.finditer(sql_content):
        if match.group(1).lower() != table_name.lower():
            continue

        records = _rows_to_dicts(match.group(2), _parse_insert_values(match.group(3)))
        
        for r in records:
            processed_data = {}
            for raw_key, val in r.items():
                if raw_key in attr_by_name:
                    attr_key = attr_by_name[raw_key]
                    # Làm sạch chuỗi: xóa dấu nháy và khoảng trắng thừa
                    val_str = val.strip("'").strip() 
                    
                    # --- XỬ LÝ ENUM TẬP TRUNG ---
                    # 1. Xử lý cột 'status' cho bảng orders và tables
                    if attr_key == "status":
                        if table_name == "orders":
                            order_status_map = {
                                "Pending confirmation": OrderStatus.PENDING,
                                "Pending": OrderStatus.PENDING,
                                "Confirmed": OrderStatus.CONFIRMED,
                                "Preparing": OrderStatus.PREPARING,
                                "Shipping": OrderStatus.SHIPPING,
                                "Completed": OrderStatus.COMPLETED,
                                "Cancelled": OrderStatus.CANCELLED,
                                "Unpaid": OrderStatus.UNPAID,
                            }
                            processed_data[attr_key] = order_status_map.get(val_str) or OrderStatus(val_str.upper())
                        elif table_name == "tables":
                            status_map = {"Booked": TableStatus.RESERVED, "Taken": TableStatus.OCCUPIED}
                            processed_data[attr_key] = status_map.get(val_str) or TableStatus(val_str)
                        else:
                            processed_data[attr_key] = val_str

                            
                    # 2. Xử lý cột 'category' cho bảng discount
                    elif attr_key == "category" and table_name == "discount":
                        try:
                            processed_data[attr_key] = DiscountCategory(val_str)
                        except ValueError:
                            processed_data[attr_key] = DiscountCategory(val_str.upper())
                    
                    # --- XỬ LÝ CÁC KIỂU DỮ LIỆU KHÁC ---
                    elif val_str.upper() == "NULL":
                        processed_data[attr_key] = None
                    elif attr_key in TYPE_CONVERTERS:
                        processed_data[attr_key] = TYPE_CONVERTERS[attr_key](val_str)
                    elif raw_key in TYPE_CONVERTERS:
                        processed_data[attr_key] = TYPE_CONVERTERS[raw_key](val_str)
                    else:
                        processed_data[attr_key] = val_str

            # If table is 'tables' and fields are missing, set defaults
            if table_name == "tables":
                if "number" not in processed_data or processed_data["number"] is None:
                    processed_data["number"] = processed_data.get("id", 1)
                if "minCapacity" not in processed_data or processed_data["minCapacity"] is None:
                    processed_data["minCapacity"] = 2
                if "seats" not in processed_data or processed_data["seats"] is None:
                    processed_data["seats"] = 4
                if "maxCapacity" not in processed_data or processed_data["maxCapacity"] is None:
                    processed_data["maxCapacity"] = 4

            # If table is 'customer' or 'staff', set default User attributes
            if table_name in ("customer", "staff"):
                u_id = processed_data.get("id", 1)
                prefix = "customer" if table_name == "customer" else "staff"
                if table_name == "staff":
                    u_id += 1000
                    processed_data["id"] = u_id
                    processed_data["roleID"] = processed_data.get("roleID", 2)
                if "username" not in processed_data or not processed_data["username"]:
                    processed_data["username"] = f"{prefix}_{u_id}"
                if "email" not in processed_data or not processed_data["email"]:
                    processed_data["email"] = f"{prefix}_{u_id}@example.com"
                if "password" not in processed_data or not processed_data["password"]:
                    processed_data["password"] = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW"

            # If table is 'orders', set defaults for missing financial fields
            if table_name == "orders":
                tp = processed_data.get("totalPrice", 0.0)
                if "subtotal" not in processed_data or processed_data["subtotal"] is None:
                    processed_data["subtotal"] = tp
                if "tax" not in processed_data or processed_data["tax"] is None:
                    processed_data["tax"] = 0.0
                if "delivery" not in processed_data or processed_data["delivery"] is None:
                    processed_data["delivery"] = 0.0

            # If table is 'reviews', map customerID/customer_id to userID
            if table_name == "reviews":
                cid = processed_data.pop("customerID", None) or processed_data.pop("customer_id", None)
                if cid is not None:
                    processed_data["userID"] = cid

            # If table is 'discount', ensure dateBegin and dateEnd are datetime objects
            if table_name == "discount":
                if "dateBegin" in processed_data and isinstance(processed_data["dateBegin"], str):
                    processed_data["dateBegin"] = datetime.fromisoformat(processed_data["dateBegin"].strip("'"))
                if "dateEnd" in processed_data and isinstance(processed_data["dateEnd"], str):
                    processed_data["dateEnd"] = datetime.fromisoformat(processed_data["dateEnd"].strip("'"))

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
            ("customer", User),
            ("staff", User),
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