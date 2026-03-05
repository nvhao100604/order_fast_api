from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        # Tự động chuyển đổi snake_case từ DB thành camelCase cho Frontend
        alias_generator=to_camel,
        # Cho phép dùng cả phoneNumber và phone_number khi khởi tạo Schema
        populate_by_name=True 
    )