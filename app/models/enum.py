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
    RESERVED = "RESERVED"  # DEPRECATED: Do not write RESERVED into DB anymore; compute dynamically in API displayStatus
    PAYING = "PAYING"
    CLEANING = "CLEANING"

class FloorItemKind(str, Enum):
    TABLE = "TABLE"
    PILLAR = "PILLAR"
    BAR = "BAR"
    DOOR = "DOOR"
    STAIRS = "STAIRS"

class TableShape(str, Enum):
    SQUARE = "SQUARE"
    ROUND = "ROUND"
    LONG = "LONG"

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