from typing import List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, allow_internal
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryFilter, CategoryResponse
from app.schemas.response import ResponseSchema
from app.services import category as categories_services

public_router = APIRouter()
private_router = APIRouter(dependencies=[Depends(allow_internal)])

# Để tương thích ngược với router.py nếu import category.router
router = public_router

@public_router.get(
    "",
    response_model=ResponseSchema[List[CategoryResponse]],
    summary="Get Categories",
    description="Retrieve a list of all categories.",
)
async def get_categories(
    filters: CategoryFilter = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    filter_dict = filters.model_dump(exclude_none=True)
    categories, total = categories_services.get_categories(
        filters=filter_dict,
        page=page,
        limit=limit,
        db=db
    )

    return ResponseSchema[List[CategoryResponse]](
        success=True,
        data=categories,
        message="Get category list successfully.",
        meta={
            "page": page,
            "limit": limit,
            "total": total
        }
    )

@private_router.post(
    "",
    response_model=ResponseSchema[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Admin/Staff creates a new dish category."
)
async def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db)
):
    new_cat = categories_services.create_category_service(db=db, data=data)
    return ResponseSchema[CategoryResponse](
        success=True,
        message="Category created successfully.",
        data=new_cat
    )

@private_router.put(
    "/{id}",
    response_model=ResponseSchema[CategoryResponse],
    summary="Update category by ID",
    description="Admin/Staff updates an existing dish category."
)
async def update_category(
    data: CategoryUpdate,
    id: int = Path(..., ge=1, description="Category ID"),
    db: Session = Depends(get_db)
):
    updated_cat = categories_services.update_category_service(db=db, category_id=id, data=data)
    return ResponseSchema[CategoryResponse](
        success=True,
        message="Category updated successfully.",
        data=updated_cat
    )

@private_router.delete(
    "/{id}",
    response_model=ResponseSchema[CategoryResponse],
    summary="Delete category by ID",
    description="Admin/Staff deletes a dish category."
)
async def delete_category(
    id: int = Path(..., ge=1, description="Category ID"),
    db: Session = Depends(get_db)
):
    deleted_cat = categories_services.delete_category_service(db=db, category_id=id)
    return ResponseSchema[CategoryResponse](
        success=True,
        message="Category deleted successfully.",
        data=deleted_cat
    )