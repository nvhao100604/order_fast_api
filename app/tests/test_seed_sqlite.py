from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.db import Base
from app.models import Dish, Category

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql" / "mysql"

SQLITE_DB = "sqlite:///sql/sqlite/test_seed.db"

def mysql_to_sqlite(sql: str) -> str:
    sql = sql.replace("INSERT IGNORE", "INSERT OR IGNORE")
    sql = sql.replace("`", "")
    sql = sql.replace("ENGINE=InnoDB", "")
    sql = sql.replace("AUTO_INCREMENT", "AUTOINCREMENT")

    if "ON DUPLICATE KEY UPDATE" in sql:
        sql = sql.split("ON DUPLICATE KEY UPDATE")[0]

    return sql


def clear_all_data(engine):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM dish"))
        conn.execute(text("DELETE FROM categories"))


def run_mysql_sql_on_sqlite(engine, filename: str):
    sql_path = SQL_DIR / filename

    with open(sql_path, "r", encoding="utf-8") as f:
        raw_sql = f.read()

    sqlite_sql = mysql_to_sqlite(raw_sql)

    with engine.begin() as conn:
        conn.execute(text(sqlite_sql))


def test_seed_sqlite_from_mysql_sql():
    engine = create_engine(
        SQLITE_DB,
        connect_args={"check_same_thread": False},
    )

    SessionLocal = sessionmaker(bind=engine)

    # 1️⃣ Create tables (1 lần là đủ)
    Base.metadata.create_all(bind=engine)

    # 2️⃣ Clear data cũ
    clear_all_data(engine)

    # 3️⃣ Run seed từ SQL MySQL
    run_mysql_sql_on_sqlite(engine, "website_order.sql")

    # 4️⃣ Verify
    db = SessionLocal()

    categories = db.query(Category).all()
    dishes = db.query(Dish).all()

    assert len(categories) > 0
    assert len(dishes) > 0

    db.close()

if __name__ == "__main__":
    test_seed_sqlite_from_mysql_sql()