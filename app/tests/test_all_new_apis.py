from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.user import User
from app.models.catalog import Category
from app.models.ordering import Table
from app.models.enum import Status, TableStatus
from app.schemas.user import UserCreate, UserUpdate, UserAdminUpdate, SendOTPRequest, VerifyOTPRequest, ResetPasswordRequest
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.ordering import TableCreate
from app.services import auth as auth_services
from app.services import category as category_services
from app.services import table as table_services
from app.crud import user as user_crud

def test_new_features():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        # 1. Test User Creation & Profile Update
        u_create = UserCreate(
            username="testuser",
            name="Test User",
            email="testuser@example.com",
            phoneNumber="0123456789",
            password="Password123!"
        )
        user = auth_services.create_new_user(db, u_create)
        assert user.id is not None
        assert user.roleID == 3
        print("1. User Registration OK!")

        # 2. Test User Profile Update
        updated_user = user_crud.update_user(db, user.id, {"name": "Updated Name", "address": "123 St"})
        assert updated_user.name == "Updated Name"
        assert updated_user.address == "123 St"
        print("2. User Profile Update OK!")

        # 3. Test Forgot Password OTP flow
        otp = auth_services.send_forgot_password_otp(db, "testuser@example.com")
        assert len(otp) == 6
        assert auth_services.verify_forgot_password_otp("testuser@example.com", otp) is True
        
        reset_user = auth_services.reset_password_with_otp(db, "testuser@example.com", otp, "NewSecretPassword123!")
        assert reset_user is not None
        print("3. Forgot Password OTP Flow OK!")

        # 4. Test Category Admin CRUD
        cat_create = CategoryCreate(name="Khai vị")
        cat = category_services.create_category_service(db, cat_create)
        assert cat.id is not None
        assert cat.name == "Khai vị"

        updated_cat = category_services.update_category_service(db, cat.id, CategoryUpdate(name="Món Khai Vị"))
        assert updated_cat.name == "Món Khai Vị"

        cats, count = category_services.get_categories(db, filters={})
        assert count == 1
        print("4. Category Admin CRUD OK!")

        # 5. Test Table POST
        tbl_create = TableCreate(number=10, minCapacity=2, maxCapacity=6, status=TableStatus.EMPTY)
        tbl = table_services.create_table_service(db, tbl_create)
        assert tbl.id is not None
        assert tbl.number == 10
        print("5. Table POST OK!")

        # 6. Test Admin User CRUD
        users, u_count = user_crud.get_users(db, filters={})
        assert u_count == 1

        admin_updated = user_crud.update_user(db, user.id, {"roleID": 1, "status": Status.ACTIVE})
        assert admin_updated.roleID == 1
        print("6. Admin User Management CRUD OK!")

        print("\n🎉 ALL NEW API BACKEND TESTS PASSED SUCCESSFULLY!")

    finally:
        db.close()

if __name__ == "__main__":
    test_new_features()
