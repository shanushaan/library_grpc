from enum import Enum

class RequestType(str, Enum):
    ISSUE = "ISSUE"
    RETURN = "RETURN"

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class TransactionStatus(str, Enum):
    BORROWED = "BORROWED"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"