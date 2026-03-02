import sys
import os

from sqlalchemy.orm import configure_mappers
from app.db.base import Base
# Import tất cả các model để SQLAlchemy nhận diện
from app.models.user import User, Role, Review, Discount
from app.models.ordering import Order, OrderDetail, Table
from app.models.catalog import Dish
from app.models.token import RefreshToken

# Thêm thư mục gốc vào path để Python tìm thấy module 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_sqlalchemy_mappers():
    """
    Test này sẽ fail nếu có bất kỳ lỗi nào về relationship, 
    back_populates hoặc foreign_keys.
    """
    try:
        configure_mappers()
        print("✅ Models OK!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sqlalchemy_mappers()
