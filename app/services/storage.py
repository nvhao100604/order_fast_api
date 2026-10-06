from typing import Optional
from fastapi import HTTPException, status
from postgrest import APIError
from supabase import StorageException, create_client, Client
from app.core.config import get_settings

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Lấy hoặc khởi tạo Supabase Client (Lazy initialization)"""
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        url = settings.SUPABASE_URL or "https://placeholder.supabase.co"
        key = settings.SUPABASE_KEY or "placeholder-key"
        _supabase_client = create_client(url, key)
    return _supabase_client

async def upload_image_to_storage(file_name: str, file_content: bytes):
    """Hàm đẩy ảnh lên Bucket và trả về URL công khai"""
    try:
        supabase = get_supabase_client()
        bucket_name = "dish_images"
        path = f"images/{file_name}"
        response = supabase.storage.from_(bucket_name).upload(
            path=path,
            file=file_content,
            file_options={"content-type": "image/jpeg"}
        )
        image_url = supabase.storage.from_(bucket_name).get_public_url(path)
        return image_url

    except StorageException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Storage error: {e.message}"
        )

    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Access denied."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected system error occurred."
        )
