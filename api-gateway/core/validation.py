import re

# Validation functions
def validate_positive_integer(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value

def validate_username(username: str) -> str:
    if not username or len(username.strip()) < 3:
        raise ValueError("Username must be at least 3 characters long")
    if not re.match(r'^[a-zA-Z0-9_]+$', username.strip()):
        raise ValueError("Username can only contain letters, numbers, and underscores")
    return username.strip()

def validate_password(password: str) -> str:
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password

def validate_request_type(request_type: str) -> str:
    valid_types = ["ISSUE", "RETURN"]
    if request_type.upper() not in valid_types:
        raise ValueError(f"Request type must be one of: {', '.join(valid_types)}")
    return request_type.upper()