from enum import Enum

class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BANNED = "BANNED"

class DiscountCategory(str, Enum):
    ORDER = "ORDER"     
    DISH = "DISH"      
    CUSTOMER = "CUSTOMER"

class TableStatus(str, Enum):
    EMPTY = "EMPTY"
    OCCUPIED  = "OCCUPIED"
    DELETED = "DELETED"
    RESERVED = "RESERVED"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    SHIPPING ="SHIPPING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    UNPAID = "UNPAID"

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"