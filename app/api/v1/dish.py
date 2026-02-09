from fastapi import APIRouter, Depends, File, Path, Query, UploadFile, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas.dish import DishCreate, DishFilter, DishUpdate
from app.services import dish as dish_service
from app.schemas import DishResponse
from app.schemas.response import ResponseSchema
from app.services.storage import upload_image_to_storage

router = APIRouter()

@router.get(
    "", 
    response_model=ResponseSchema[List[DishResponse]],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Get Dishes with Pagination",
    description="Get a paginated list of dishes from the database."
)
async def get_dishes(
    filters: DishFilter = Depends(),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Endpoint lấy danh sách món ăn"""
    filter_dict = filters.model_dump(exclude_none=True)
    dishes, total = dish_service.get_all_dishes(db, filters=filter_dict, page=page, limit=limit)

    return ResponseSchema[List[DishResponse]](
        data=dishes,
        message="Get dish list successfully.",
        meta={
            "page": page, 
            "limit": limit, 
            "total": total
        }
    )


@router.post(
    "",
    response_model=ResponseSchema[DishResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Create a New Dish",
    description="Create a new dish in the database."
)
async def post_dish(
    dish: DishCreate,
    db: Session = Depends(get_db)
):
    """Endpoint thêm món ăn mới"""
    new_dish = dish_service.post_dish(db, dish)
    return ResponseSchema[DishResponse](
        data=new_dish,
        message="Create dish successfully",
    )


@router.post("/upload")
async def upload_dish_image(file: UploadFile = File(...)):
    # Đọc nội dung file ảnh
    content = await file.read()
    
    # Upload lên Cloud và lấy URL
    img_url = await upload_image_to_storage(file.filename, content)
    
    return {
        "success": True,
        "message": "Upload successfully.",
        "data": {"imgUrl": img_url}
    }

@router.get(
    "/{id}",
    response_model=ResponseSchema[DishResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Get Dish by ID",
    description="Get a specific dish by its ID."
)
async def get_dish(
    id: int = Path(..., description="ID of specific dish", ge=1),
    db: Session = Depends(get_db)
):
    dish = dish_service.get_dish(db, id)
    if not dish:
        return ResponseSchema[DishResponse](
            data=None,
            message="Dish not found",
        )
    return ResponseSchema[DishResponse](
        data=dish,
        message=f"Get dish successfully with id: {id}",
    )


@router.put(
        "/{id}",
    response_model=ResponseSchema[DishResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Update Dish by ID",
    description="Update an existing dish by its ID."
)
async def put_dish(
    id: int = Path(..., description="ID of the dish to update", ge=1),
    updated_dish: DishCreate = ...,
    db: Session = Depends(get_db)
):
    """Endpoint cập nhật món ăn theo ID"""
    updated_dish_instance = dish_service.put_dish(db, id, updated_dish)
    if not updated_dish_instance:
        return ResponseSchema[DishResponse](
            data=None,
            message="Dish not found",
        )
    return ResponseSchema[DishResponse](
        data=updated_dish_instance,
        message=f"Update dish successfully with id: {id}",
    )


@router.patch(
    "/{id}",
    response_model=ResponseSchema[DishResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Partially Update Dish by ID",
    description="Partially update fields of an existing dish by its ID."
)
async def patch_dish(
    id: int = Path(..., description="ID of the dish to update", ge=1),
    updated_fields: DishUpdate = ...,
    db: Session = Depends(get_db)
):
    """Endpoint cập nhật một số trường của món ăn theo ID"""
    updated_dish_instance = dish_service.patch_dish(db, id, updated_fields)
    if not updated_dish_instance:
        return ResponseSchema[DishResponse](
            data=None,
            message="Dish not found",
        )
    return ResponseSchema[DishResponse](
        data=updated_dish_instance,
        message=f"Update dish successfully with id: {id}",
    )

@router.delete(
        "/{id}",
    response_model=ResponseSchema[DishResponse],
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ResponseSchema}},
    summary="Delete Dish by ID",
    description="Delete a dish from the database by its ID."
)
async def delete_dish(
    id: int = Path(..., description="ID of the dish to delete", ge=1),
    db: Session = Depends(get_db)
):
    """Endpoint xoá món ăn theo ID"""
    deleted_dish = dish_service.delete_dish(db, id)
    if not deleted_dish:
        return ResponseSchema[DishResponse](
            data=None,
            message="Dish not found",
        )
    return ResponseSchema[DishResponse](
        data=deleted_dish,
        message=f"Delete dish successfully with id: {id}",
    )