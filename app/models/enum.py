import enum

# class UserRole(enum.Enum):
#     ADMIN = "admin"
#     STAFF = "staff"
#     CUSTOMER = "customer"
    
class Status(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class DiscountCategory(str, enum.Enum):
    ORDER = "order"     
    DISH = "dish"      
    CUSTOMER = "customer"

class TableStatus(str, enum.Enum):
    Empty = "Empty"
    Booked = "Booked"
    Deleted = "Deleted"
    Taken = "Taken"

class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PREPARING = "Preparing"
    SHIPPING ="Out for Delivery"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    UNPAID = "Pending Payment"