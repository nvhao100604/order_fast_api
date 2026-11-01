import pytest
from fastapi import HTTPException
from app.api.deps import allow_internal, allow_admin, RoleChecker
from app.core.constants import RoleID
from app.models.user import User
from app.models.enum import Status


def test_customer_forbidden_on_allow_internal():
    customer = User(
        id=99,
        username="customer_user",
        roleID=RoleID.CUSTOMER,
        status=Status.ACTIVE,
    )
    with pytest.raises(HTTPException) as exc:
        allow_internal(current_user=customer)
    assert exc.value.status_code == 403


def test_staff_allowed_on_allow_internal():
    staff = User(
        id=10,
        username="staff_user",
        roleID=RoleID.STAFF,
        status=Status.ACTIVE,
    )
    user = allow_internal(current_user=staff)
    assert user.id == 10
    assert user.roleID == RoleID.STAFF


def test_admin_allowed_on_allow_internal():
    admin = User(
        id=1,
        username="admin_user",
        roleID=RoleID.ADMIN,
        status=Status.ACTIVE,
    )
    user = allow_internal(current_user=admin)
    assert user.id == 1
    assert user.roleID == RoleID.ADMIN


def test_staff_forbidden_on_allow_admin():
    staff = User(
        id=10,
        username="staff_user",
        roleID=RoleID.STAFF,
        status=Status.ACTIVE,
    )
    with pytest.raises(HTTPException) as exc:
        allow_admin(current_user=staff)
    assert exc.value.status_code == 403
