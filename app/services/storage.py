from fastapi import HTTPException, status
from postgrest import APIError
from supabase import StorageException, create_client, Client
from app.core.config import get_settings

# Khởi tạo client Supabase
supabase: Client = create_client(get_settings().SUPABASE_URL, get_settings().SUPABASE_KEY)

async def upload_image_to_storage(file_name: str, file_content: bytes):
    """Hàm đẩy ảnh lên Bucket và trả về URL công khai"""
    try:
        bucket_name = "dish_images" # Tên bucket bạn vừa tạo
        
        # 1. Đẩy file lên Supabase Storage
        path = f"images/{file_name}"
        response = supabase.storage.from_(bucket_name).upload(
            path=path,
            file=file_content,
            file_options={"content-type": "image/jpeg"}
        )
        # 2. Lấy URL công khai để lưu vào cột imgUrl trong DB
        image_url = supabase.storage.from_(bucket_name).get_public_url(path)
        return image_url
    
    except StorageException as e:
    # Thường là lỗi do File (quá lớn, trùng tên) hoặc cấu hình Bucket
    # Nếu là lỗi do user, dùng 400. Nếu lỗi Bucket không tồn tại, dùng 500.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Storage error: {e.message}"
        )

    except APIError as e:
        # Đây là lỗi nghiêm trọng về cấu hình (Credential)
        # User không thể làm gì để sửa lỗi này -> Dùng 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Access denied."
        )

    except Exception as e:
        # Lỗi "trên trời rơi xuống"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected system error occurred."
        )
