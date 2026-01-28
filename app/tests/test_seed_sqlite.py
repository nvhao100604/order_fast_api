from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.seed_loader import (
    load_categories_from_sql,
    load_dishes_from_sql,
)

BASE_DIR = Path(__file__).resolve().parents[2]
SQLITE_DB = f"sqlite:///{BASE_DIR}/sql/sqlite/test_seed.db"


def clear_all_data(engine):
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


def test_seed_sqlite_from_mysql_sql():
    engine = create_engine(
        SQLITE_DB,
        connect_args={"check_same_thread": False},
    )

    SessionLocal = sessionmaker(bind=engine)

    # 1️⃣ Tạo table từ model
    Base.metadata.create_all(bind=engine)

    # 2️⃣ Clear data cũ
    clear_all_data(engine)

    # 3️⃣ Load data từ SQL dump
    categories = load_categories_from_sql("website_order.sql")
    dishes = load_dishes_from_sql("website_order.sql")

    # 4️⃣ Insert vào SQLite
    with SessionLocal() as db:
        db.add_all(categories)
        db.commit()

        db.add_all(dishes)
        db.commit()

    assert len(categories) > 0
    assert len(dishes) > 0
    print(f"Seeded {len(categories)} categories and {len(dishes)} dishes into SQLite.")