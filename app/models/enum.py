from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class DiscountCategory(str, Enum):
    ORDER = "order"     
    DISH = "dish"      
    CUSTOMER = "customer"

class TableStatus(str, Enum):
    EMPTY = "Empty"
    OCCUPIED  = "Occupied"
    DELETED = "Deleted"
    RESERVED = "Reserved"

class OrderStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PREPARING = "Preparing"
    SHIPPING ="Out for Delivery"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    UNPAID = "Pending Payment"

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"