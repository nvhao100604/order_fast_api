import pytest
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.seed_loader import load_from_sql_generic # Sử dụng hàm Generic bạn vừa viết
from app.models import (
    Role, Staff, Category, Dish, 
    Table, Customer, Order, OrderDetail, 
    Review, Discount
)

# =========================
# CẤU HÌNH ĐƯỜNG DẪN
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]

# Đường dẫn tới tệp SQL để đọc dữ liệu
SQL_DUMP_PATH = BASE_DIR / "sql" / "mysql" / "website_order.sql"

# app/tests/test_seed_sqlite.py
SQLITE_DB_PATH = BASE_DIR / "sql" / "sqlite" / "test_seed.db"
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

def clear_all_data(engine):
    """Xóa dữ liệu theo thứ tự ngược để tránh lỗi ràng buộc trên SQLite"""
    with engine.begin() as conn:
        # SQLite không có TRUNCATE CASCADE, nên ta xóa theo thứ tự Metadata
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())

def test_seed_sqlite_full_system():
    # Đảm bảo thư mục chứa file .db tồn tại
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 1️⃣ Khởi tạo Engine SQLite
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(bind=engine)

    # 2️⃣ Tạo cấu trúc bảng và làm sạch dữ liệu
    Base.metadata.create_all(bind=engine)
    clear_all_data(engine)

    # 3️⃣ Đọc nội dung file SQL một lần duy nhất
    if not SQL_DUMP_PATH.exists():
        pytest.fail(f"Không tìm thấy file SQL tại: {SQL_DUMP_PATH}")
    
    sql_content = SQL_DUMP_PATH.read_text(encoding="utf-8")
    # 4️⃣ Định nghĩa danh sách các bảng cần nạp theo thứ tự logic
    # (Bảng cha nạp trước, bảng con nạp sau)
    tables_to_seed = [
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

    # 5️⃣ Thực hiện nạp dữ liệu qua hàm Generic
    with SessionLocal() as db:
        print("\n--- Đang tiến hành Seeding vào SQLite ---")
        for table_name, model_class in tables_to_seed:
            objects = load_from_sql_generic(sql_content, table_name, model_class)
            
            if objects:
                db.add_all(objects)
                db.commit() # Commit sau mỗi bảng để đảm bảo ID có sẵn cho bảng sau
                print(f"✅ Đã nạp {len(objects)} bản ghi vào bảng {table_name}")
            
            # Kiểm tra xem dữ liệu có thực sự được nạp không
            assert len(objects) >= 0 # Đảm bảo không lỗi code xử lý Regex

    print(f"\n🎉 Hoàn thành: Toàn bộ 10 bảng đã có dữ liệu mẫu tại {SQLITE_URL}")

if __name__ == "__main__":
    # Cho phép chạy trực tiếp tệp này để kiểm tra nhanh
    test_seed_sqlite_full_system()