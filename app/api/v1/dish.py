from fastapi import APIRouter

router = APIRouter()

@router.get(
        '',
        summary="List dishes",
        description="Trả về danh sách các món ăn"
    )
def list_dishes():
    return {
        "dishes": [
            {"id": 1, "name": "Spaghetti Carbonara", "price": 12.99},
            {"id": 2, "name": "Margherita Pizza", "price": 10.99},
        ]
    }