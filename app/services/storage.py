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
        # Lỗi: Bucket không tồn tại hoặc trùng tên file
        raise ValueError(f"Storage error: {e.message}")
    except APIError as e:
        # Lỗi: Sai SUPABASE_KEY (service_role)
        raise ValueError("Access denied: Invalid API credentials.")
    except Exception as e:
        # Lỗi hệ thống không mong muốn
        raise ValueError("An unexpected error occurred during file upload.")
