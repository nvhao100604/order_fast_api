import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Type
from sqlalchemy import text

# Sử dụng SessionLocal đã kết nối tới Postgres qua .env
from app.db.session import SessionLocal
from app.db.seed_loader import load_from_sql_generic # Hàm generic đã tách
from app.models import (
    Role, Staff, Category, Dish, 
    Table, Customer, Order, OrderDetail, 
    Review, Discount
)

# =========================
# CẤU HÌNH ĐƯỜNG DẪN
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
SQL_FILE_PATH = BASE_DIR / "sql" / "mysql" / "website_order.sql"

def run_seed_postgres():
    if not SQL_FILE_PATH.exists():
        print(f"❌ Không tìm thấy file SQL tại: {SQL_FILE_PATH}")
        return

    db = SessionLocal()
    # Đọc nội dung file SQL
    sql_content = SQL_FILE_PATH.read_text(encoding="utf-8")

    # Thứ tự nạp cực kỳ quan trọng để không lỗi khóa ngoại (Foreign Key)
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

    try:
        print("--- Đang chuẩn bị nạp dữ liệu vào PostgreSQL ---")

        for table_name, model_class in table_order:
            print(f"🔄 Đang xử lý bảng: {table_name}...")
            
            # 1. Dọn dẹp dữ liệu cũ & reset ID về 1 (Postgres cực mạnh ở lệnh này)
            # Dùng CASCADE để tự động xử lý các bảng liên quan
            db.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
            
            # 2. Sử dụng hàm Generic để bóc tách dữ liệu từ file SQL
            objects = load_from_sql_generic(sql_content, table_name, model_class)
            
            if objects:
                db.add_all(objects)
                db.commit() # Commit sau mỗi bảng để ID có hiệu lực cho bảng sau
                print(f"   ✅ Đã nạp {len(objects)} bản ghi.")
            else:
                print(f"   ⚠️ Không tìm thấy dữ liệu cho {table_name} trong file SQL.")

        print("\n🏆 CHÚC MỪNG! Toàn bộ 11 bảng PostgreSQL đã được làm sạch và nạp dữ liệu mới.")

    except Exception as e:
        print(f"❌ LỖI KHI NẠP DỮ LIỆU: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed_postgres()