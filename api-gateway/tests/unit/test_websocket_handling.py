import pytest
from unittest.mock import AsyncMock, MagicMock
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.notification_service import NotificationService

pytestmark = pytest.mark.asyncio

class TestWebSocketHandling:
    """Test WebSocket connection and notification handling"""
    
    def test_notification_service_initialization(self):
        service = NotificationService()
        assert service.user_connections == {}
    
    def test_add_multiple_connections(self):
        service = NotificationService()
        ws1 = MagicMock()
        ws2 = MagicMock()
        
        service.add_connection("user1", ws1)
        service.add_connection("user2", ws2)
        
        assert len(service.user_connections) == 2
        assert service.user_connections["user1"] == ws1
        assert service.user_connections["user2"] == ws2
    
    def test_remove_nonexistent_connection(self):
        service = NotificationService()
        # Should not raise error
        service.remove_connection("nonexistent")
        assert len(service.user_connections) == 0
    
    def test_overwrite_existing_connection(self):
        service = NotificationService()
        ws1 = MagicMock()
        ws2 = MagicMock()
        
        service.add_connection("user1", ws1)
        service.add_connection("user1", ws2)  # Overwrite
        
        assert len(service.user_connections) == 1
        assert service.user_connections["user1"] == ws2
    
    async def test_send_notification_success(self):
        service = NotificationService()
        mock_ws = AsyncMock()
        service.user_connections["123"] = mock_ws
        
        notification = {"type": "TEST", "message": "Hello"}
        await service.send_notification(123, notification)
        
        mock_ws.send_text.assert_called_once_with(json.dumps(notification))
    
    async def test_send_notification_connection_error_cleanup(self):
        service = NotificationService()
        mock_ws = AsyncMock()
        mock_ws.send_text.side_effect = Exception("Connection closed")
        service.user_connections["123"] = mock_ws
        
        notification = {"type": "TEST", "message": "Hello"}
        await service.send_notification(123, notification)
        
        # Connection should be removed after error
        assert "123" not in service.user_connections
    
    async def test_send_notification_to_multiple_users(self):
        service = NotificationService()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        service.user_connections["1"] = mock_ws1
        service.user_connections["2"] = mock_ws2
        
        notification = {"type": "BROADCAST", "message": "Hello all"}
        
        await service.send_notification(1, notification)
        await service.send_notification(2, notification)
        
        mock_ws1.send_text.assert_called_once_with(json.dumps(notification))
        mock_ws2.send_text.assert_called_once_with(json.dumps(notification))