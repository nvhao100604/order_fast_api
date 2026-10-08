# app/api/v1/table_ops.py
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import table_ops
from app.schemas.ordering import TableStatusResponse
from app.schemas.response import ResponseSchema

router = APIRouter()


class MergeRequest(BaseModel):
    tableIDs: List[int]


@router.post("/{table_id}/open", response_model=ResponseSchema[TableStatusResponse])
def open_table_endpoint(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    table = table_ops.open_table(db, table_id)
    return ResponseSchema[TableStatusResponse](
        data=table, message=f"Table {table_id} opened."
    )


@router.post("/merge", response_model=ResponseSchema[List[TableStatusResponse]])
def merge_tables_endpoint(
    body: MergeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tables = table_ops.merge_tables(db, body.tableIDs)
    return ResponseSchema[List[TableStatusResponse]](
        data=tables, message="Tables merged."
    )


@router.post("/{table_id}/split", response_model=ResponseSchema[TableStatusResponse])
def split_table_endpoint(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    table = table_ops.split_table(db, table_id)
    return ResponseSchema[TableStatusResponse](
        data=table, message=f"Table {table_id} split."
    )


@router.post("/{table_id}/close", response_model=ResponseSchema[TableStatusResponse])
def close_table_endpoint(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    table = table_ops.close_table(db, table_id)
    return ResponseSchema[TableStatusResponse](
        data=table, message=f"Table {table_id} closed."
    )
