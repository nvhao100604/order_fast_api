# app/tests/test_idempotency_model.py
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.enum import IdempotencyStatus
from app.models.idempotency import IdempotencyRecord


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_idempotency_record(db):
    now = datetime.now(timezone.utc)
    record = IdempotencyRecord(
        key="test-key-123",
        userID=None,
        requestPath="/api/v1/orders",
        requestHash="hash-abc-456",
        status=IdempotencyStatus.PENDING,
        lockedUntil=now + timedelta(seconds=60),
    )
    db.add(record)
    db.commit()

    saved = db.query(IdempotencyRecord).filter_by(key="test-key-123").first()
    assert saved is not None
    assert saved.key == "test-key-123"
    assert saved.status == IdempotencyStatus.PENDING
    assert saved.responseCode is None
