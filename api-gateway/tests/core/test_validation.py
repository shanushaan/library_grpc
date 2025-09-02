import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.validation import validate_username, validate_password, validate_positive_integer, validate_request_type

class TestValidation:
    """Test core validation functions"""
    
    def test_validate_username_success(self):
        assert validate_username("testuser") == "testuser"
        assert validate_username("test_user123") == "test_user123"
    
    def test_validate_username_too_short(self):
        with pytest.raises(ValueError) as exc_info:
            validate_username("ab")
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_validate_username_invalid_chars(self):
        with pytest.raises(ValueError) as exc_info:
            validate_username("test@user")
        assert "letters, numbers, and underscores" in str(exc_info.value)
    
    def test_validate_password_success(self):
        assert validate_password("password123") == "password123"
    
    def test_validate_password_too_short(self):
        with pytest.raises(ValueError) as exc_info:
            validate_password("123")
        assert "at least 6 characters" in str(exc_info.value)
    
    def test_validate_positive_integer_success(self):
        assert validate_positive_integer(5, "Test ID") == 5
    
    def test_validate_positive_integer_zero(self):
        with pytest.raises(ValueError) as exc_info:
            validate_positive_integer(0, "Test ID")
        assert "must be a positive integer" in str(exc_info.value)
    
    def test_validate_request_type_success(self):
        assert validate_request_type("ISSUE") == "ISSUE"
        assert validate_request_type("issue") == "ISSUE"
        assert validate_request_type("RETURN") == "RETURN"
    
    def test_validate_request_type_invalid(self):
        with pytest.raises(ValueError) as exc_info:
            validate_request_type("INVALID")
        assert "ISSUE, RETURN" in str(exc_info.value)