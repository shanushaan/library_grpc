from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.notification_service import notification_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket('/')
async def websocket_endpoint(websocket: WebSocket):
    # Validate WebSocket connection parameters
    query_params = dict(websocket.query_params)
    user_id = query_params.get('userId')
    
    if user_id and not user_id.isdigit():
        logger.warning("WebSocket connection with invalid userId format", extra={
            "user_id": user_id,
            "action": "ws_invalid_user_id_format"
        })
        await websocket.close(code=4000, reason="Invalid userId format")
        return
    
    try:
        logger.debug("WebSocket connection attempt", extra={"action": "ws_connect_start"})
        await websocket.accept()
        
        if user_id:
            notification_service.add_connection(user_id, websocket)
        else:
            logger.warning("WebSocket connection without user_id", extra={"action": "ws_no_user_id"})
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        if user_id:
            notification_service.remove_connection(user_id)
    except Exception as e:
        logger.error("WebSocket connection error", extra={
            "user_id": user_id,
            "error": str(e),
            "action": "ws_error"
        }, exc_info=True)
        if user_id:
            notification_service.remove_connection(user_id)