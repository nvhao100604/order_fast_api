from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.category import CategoryFilter, CategoryResponse
from app.schemas.response import ResponseSchema
from app.services import category as categories_services

router = APIRouter()

@router.get(
    "",
    response_model=ResponseSchema[List[CategoryResponse]],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Get Categories",
    description="Retrieve a list of all categories.",
)
async def get_categories(
    filters: CategoryFilter = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db : Session = Depends(get_db)
):
    filter_dict = filters.model_dump(exclude_none=True)
    categories, total = categories_services.get_categories(
        filters=filter_dict,
        page=page,
        limit=limit,
        db=db
    )

    return ResponseSchema[List[CategoryResponse]](
        data=categories,
        message="Get category list successfully.",
        meta={
            "page": page,
            "limit": limit,
            "total": total
        }
    )