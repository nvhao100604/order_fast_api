from sqlalchemy import create_engine, text
from app.core.config import get_settings

DATABASE_URL = get_settings().SQLALCHEMY_DATABASE_URI

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("DB connected:", result.scalar())
except Exception as e:
    print("DB connection failed:", e)
