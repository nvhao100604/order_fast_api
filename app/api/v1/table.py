from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas.ordering import TableResponse, TableStatus
from app.schemas.response import ResponseSchema
from app.services import table as table_service

public_router = APIRouter()
private_router = APIRouter()

@public_router.get(
    "", 
    response_model=ResponseSchema[List[TableResponse]],
    summary="Get Tables with Pagination",
    description="Retrieve a paginated list of tables. You can filter by status or minimum capacity."
)
async def get_tables(
    status: TableStatus = Query(None),
    minCapacity: int = Query(None, ge=1, description="Filter tables that can accommodate at least this many people"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    filters = {"status": status, "minCapacity": minCapacity}
    tables, total = table_service.get_tables(db, filters=filters, page=page, limit=limit)

    return ResponseSchema[List[TableResponse]](
        data=tables,
        message="Get table list successfully.",
        meta={"page": page, "limit": limit, "total": total}
    )

@public_router.get(
    "/{id}",
    response_model=ResponseSchema[TableResponse],
    summary="Get Table by ID",
    description="Retrieve detailed information about a specific table by its unique ID."
)
async def get_table(
    id: int = Path(..., ge=1, description="The ID of the table to retrieve"),
    db: Session = Depends(get_db)
):
    table = table_service.get_table(db, id)
    return ResponseSchema[TableResponse](
        data=table,
        message=f"Get table successfully with id: {id}"
    )

@private_router.patch(
    "/{id}/status",
    response_model=ResponseSchema[TableResponse],
    summary="Update Table Status",
    description="Quickly update the status of a table (e.g., from FREE to OCCUPIED)."
)
async def patch_table_status(
    id: int = Path(..., ge=1),
    new_status: TableStatus = Query(..., description="The new status to apply to the table"),
    db: Session = Depends(get_db)
):
    updated_table = table_service.update_table_status(db, id, new_status)
    return ResponseSchema[TableResponse](
        data=updated_table,
        message=f"Update table status to {new_status} successfully"
    )

@private_router.patch(
    "/{id}",
    response_model=ResponseSchema[TableResponse],
    summary="Partially Update Table Info",
    description="Update specific fields of a table such as its number or capacity."
)
async def patch_table(
    id: int = Path(..., ge=1),
    update_data: dict = {}, 
    db: Session = Depends(get_db)
):
    updated_table = table_service.update_table_info(db, id, update_data)
    return ResponseSchema[TableResponse](
        data=updated_table,
        message="Update table info successfully"
    )

@private_router.delete(
    "/{id}",
    response_model=ResponseSchema[TableResponse],
    summary="Delete Table",
    description="Remove a table from the system. Note: Tables with active orders cannot be deleted."
)
async def delete_table(
    id: int = Path(..., ge=1),
    db: Session = Depends(get_db)
):
    deleted_table = table_service.delete_table(db, id)
    return ResponseSchema[TableResponse](
        data=deleted_table,
        message=f"Delete table successfully with id: {id}"
    )