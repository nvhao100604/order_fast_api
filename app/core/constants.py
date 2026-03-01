from enum import Enum

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class RoleID:
    ADMIN = 1
    STAFF = 2
    CUSTOMER = 3