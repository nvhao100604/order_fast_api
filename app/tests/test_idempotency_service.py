# app/tests/test_idempotency_service.py
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.enum import IdempotencyStatus
from app.models.idempotency import IdempotencyRecord
from app.services.idempotency import (
    compute_payload_hash,
    evaluate_idempotency,
    finalize_idempotency,
    fail_idempotency,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_compute_payload_hash_consistent():
    d1 = {"b": 2, "a": 1}
    d2 = {"a": 1, "b": 2}
    assert compute_payload_hash(d1) == compute_payload_hash(d2)


def test_evaluate_first_time_creates_pending_record(db):
    h = compute_payload_hash({"foo": "bar"})
    cached, record = evaluate_idempotency(db, key="k1", user_id=1, path="/test", payload_hash=h)
    assert cached is None
    assert record.key == "k1"
    assert record.status == IdempotencyStatus.PENDING


def test_evaluate_in_progress_raises_409(db):
    h = compute_payload_hash({"foo": "bar"})
    evaluate_idempotency(db, key="k2", user_id=1, path="/test", payload_hash=h)
    
    with pytest.raises(HTTPException) as exc:
        evaluate_idempotency(db, key="k2", user_id=1, path="/test", payload_hash=h)
    assert exc.value.status_code == 409


def test_evaluate_payload_mismatch_raises_422(db):
    h1 = compute_payload_hash({"foo": "bar"})
    h2 = compute_payload_hash({"foo": "baz"})
    evaluate_idempotency(db, key="k3", user_id=1, path="/test", payload_hash=h1)

    with pytest.raises(HTTPException) as exc:
        evaluate_idempotency(db, key="k3", user_id=1, path="/test", payload_hash=h2)
    assert exc.value.status_code == 422


def test_finalize_and_evaluate_success_replays_response(db):
    h = compute_payload_hash({"foo": "bar"})
    evaluate_idempotency(db, key="k4", user_id=1, path="/test", payload_hash=h)
    finalize_idempotency(db, key="k4", response_code=201, response_data={"success": True, "id": 99})

    cached, record = evaluate_idempotency(db, key="k4", user_id=1, path="/test", payload_hash=h)
    assert cached is not None
    assert cached["code"] == 201
    assert cached["data"] == {"success": True, "id": 99}
