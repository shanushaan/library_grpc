import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.notification_service import NotificationService

class TestNotificationService:
    """Test notification service WebSocket management"""
    
    def test_add_connection(self):
        service = NotificationService()
        mock_websocket = MagicMock()
        
        service.add_connection("123", mock_websocket)
        
        assert "123" in service.user_connections
        assert service.user_connections["123"] == mock_websocket
    
    def test_remove_connection(self):
        service = NotificationService()
        mock_websocket = MagicMock()
        
        service.add_connection("123", mock_websocket)
        service.remove_connection("123")
        
        assert "123" not in service.user_connections
    
    async def test_send_notification_no_connection(self):
        service = NotificationService()
        
        # Should not raise error when user not connected
        await service.send_notification(999, {"type": "TEST", "message": "test"})
        # No assertion needed - should complete without error
    
    async def test_send_notification_dead_connection(self):
        service = NotificationService()
        mock_ws = AsyncMock()
        mock_ws.send_text.side_effect = Exception("Connection closed")
        service.user_connections["123"] = mock_ws
        
        # Should remove dead connection
        await service.send_notification(123, {"type": "TEST", "message": "test"})
        assert "123" not in service.user_connections