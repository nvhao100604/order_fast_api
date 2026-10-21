# app/services/idempotency.py
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.idempotency import IdempotencyRecord
from app.models.enum import IdempotencyStatus

LEASE_SECONDS = 60


def compute_payload_hash(payload: Any) -> str:
    """Compute deterministic SHA-256 hash for payload."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def evaluate_idempotency(
    db: Session,
    key: str,
    user_id: Optional[int],
    path: str,
    payload_hash: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[IdempotencyRecord]]:
    """
    Check key status.
    Returns:
      (cached_response, None) if key is already SUCCESS.
      (None, record) if newly created or lease refreshed (proceed).
    Raises:
      422 if key is reused with different payload hash.
      409 if key is currently being processed (PENDING and lease valid).
    """
    now = datetime.now(timezone.utc)
    record = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).first()

    if record:
        # Check payload mismatch
        if record.requestHash != payload_hash:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Idempotency-Key reused with a different request payload."
            )

        if record.status == IdempotencyStatus.SUCCESS:
            data = json.loads(record.responseBody) if record.responseBody else None
            return {"code": record.responseCode or 200, "data": data}, None

        if record.status == IdempotencyStatus.PENDING:
            locked_until = record.lockedUntil
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if now < locked_until:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A request with this Idempotency-Key is currently being processed."
                )
            # Lease expired -> allow refresh and re-run
            record.lockedUntil = now + timedelta(seconds=LEASE_SECONDS)
            db.commit()
            return None, record

        # If FAILED, reset to PENDING
        record.status = IdempotencyStatus.PENDING
        record.lockedUntil = now + timedelta(seconds=LEASE_SECONDS)
        db.commit()
        return None, record

    # Create new PENDING record
    from sqlalchemy.exc import IntegrityError
    new_record = IdempotencyRecord(
        key=key,
        userID=user_id,
        requestPath=path,
        requestHash=payload_hash,
        status=IdempotencyStatus.PENDING,
        lockedUntil=now + timedelta(seconds=LEASE_SECONDS),
    )
    db.add(new_record)
    try:
        db.commit()
        db.refresh(new_record)
        return None, new_record
    except IntegrityError:
        db.rollback()
        # Another concurrent request inserted the key in the exact same millisecond
        record = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).first()
        if record:
            if record.requestHash != payload_hash:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Idempotency-Key reused with a different request payload."
                )
            if record.status == IdempotencyStatus.SUCCESS:
                data = json.loads(record.responseBody) if record.responseBody else None
                return {"code": record.responseCode or 200, "data": data}, None
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A request with this Idempotency-Key is currently being processed."
            )
        raise



def finalize_idempotency(
    db: Session,
    key: str,
    response_code: int,
    response_data: Any
):
    """Mark record as SUCCESS and cache response body."""
    record = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).first()
    if record:
        record.status = IdempotencyStatus.SUCCESS
        record.responseCode = response_code
        record.responseBody = json.dumps(response_data, default=str)
        db.commit()


def fail_idempotency(db: Session, key: str):
    """Mark record as FAILED (or delete) so user can retry."""
    record = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).first()
    if record and record.status == IdempotencyStatus.PENDING:
        record.status = IdempotencyStatus.FAILED
        db.commit()
