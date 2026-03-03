import enum

# class UserRole(enum.Enum):
#     ADMIN = "admin"
#     STAFF = "staff"
#     CUSTOMER = "customer"
    
class Status(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class DiscountCategory(enum.Enum):
    ORDER = "order"     
    DISH = "dish"      
    CUSTOMER = "customer"

class TableStatus(enum.Enum):
    Empty = "Empty"
    Booked = "Booked"
    Deleted = "Deleted"
    Taken = "Taken"

class OrderStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PREPARING = "Preparing"
    SHIPPING ="Out for Delivery"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    UNPAID = "Pending Payment"