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

async def upload_image_to_storage(
    file_name: str,
    file_content: bytes,
    bucket_name: Optional[str] = None,
    folder: Optional[str] = None,
    content_type: str = "image/jpeg",
) -> str:
    """Hàm đẩy ảnh lên Bucket và trả về URL công khai.

    Nếu không truyền bucket_name hoặc folder, hàm sẽ tự động lấy mặc định từ Settings:
    - bucket_name: settings.SUPABASE_BUCKET_NAME
    - folder: settings.SUPABASE_STORAGE_PATH
    """
    try:
        settings = get_settings()
        supabase = get_supabase_client()
        target_bucket = bucket_name or settings.SUPABASE_BUCKET_NAME
        target_folder = folder if folder is not None else settings.SUPABASE_STORAGE_PATH

        cleaned_folder = target_folder.strip("/ ") if target_folder else ""
        path = f"{cleaned_folder}/{file_name}" if cleaned_folder else file_name

        response = supabase.storage.from_(target_bucket).upload(
            path=path,
            file=file_content,
            file_options={"content-type": content_type}
        )
        image_url = supabase.storage.from_(target_bucket).get_public_url(path)
        return image_url

    except StorageException as e:
        error_msg = (
            e.args[0].get("message")
            if e.args and isinstance(e.args[0], dict)
            else (getattr(e, "message", None) or str(e))
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Storage error: {error_msg}"
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
