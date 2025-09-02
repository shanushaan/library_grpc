import pytest
import json
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.logging_config import JSONFormatter, setup_logging

class TestJSONFormatter:
    """Test JSON logging formatter"""
    
    def test_json_formatter_basic(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=1,
            msg="Test message", args=(), exc_info=None
        )
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert parsed["service"] == "api-gateway"
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed
    
    def test_json_formatter_with_extra_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=1,
            msg="Error message", args=(), exc_info=None
        )
        record.user_id = 123
        record.action = "test_action"
        
        result = formatter.format(record)
        parsed = json.loads(result)
        
        assert parsed["user_id"] == 123
        assert parsed["action"] == "test_action"
        assert parsed["level"] == "ERROR"

class TestSetupLogging:
    """Test logging setup function"""
    
    def test_setup_logging_returns_logger(self):
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)