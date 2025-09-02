import json
import logging
from typing import Dict
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.user_connections: Dict[str, WebSocket] = {}
    
    def add_connection(self, user_id: str, websocket: WebSocket):
        """Add WebSocket connection for user"""
        self.user_connections[user_id] = websocket
        logger.info("WebSocket connection established", extra={
            "user_id": user_id,
            "action": "ws_connected",
            "total_connections": len(self.user_connections)
        })
    
    def remove_connection(self, user_id: str):
        """Remove WebSocket connection for user"""
        if user_id in self.user_connections:
            del self.user_connections[user_id]
            logger.info("WebSocket connection closed", extra={
                "user_id": user_id,
                "action": "ws_disconnected",
                "total_connections": len(self.user_connections)
            })
    
    async def send_notification(self, user_id: int, notification: dict):
        """Send notification to user via WebSocket"""
        user_id_str = str(user_id)
        logger.debug("Attempting to send notification", extra={
            "user_id": user_id,
            "notification_type": notification.get('type'),
            "action": "notification_send_start"
        })
        
        if user_id_str in self.user_connections:
            try:
                await self.user_connections[user_id_str].send_text(json.dumps(notification))
                logger.info("Notification sent successfully", extra={
                    "user_id": user_id,
                    "notification_type": notification.get('type'),
                    "action": "notification_sent"
                })
            except Exception as e:
                logger.warning("Failed to send notification - removing dead connection", extra={
                    "user_id": user_id,
                    "error": str(e),
                    "action": "notification_failed"
                })
                if user_id_str in self.user_connections:
                    del self.user_connections[user_id_str]
        else:
            logger.debug("User not connected - notification not sent", extra={
                "user_id": user_id,
                "notification_type": notification.get('type'),
                "action": "notification_no_connection"
            })

# Global notification service instance
notification_service = NotificationService()