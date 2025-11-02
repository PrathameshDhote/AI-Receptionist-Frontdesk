from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.notification_service import connection_manager

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/supervisor")
async def websocket_supervisor_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for supervisor dashboard.
    
    The supervisor dashboard connects here to receive real-time notifications about:
    - New help requests from customers
    - Request resolutions
    - Knowledge base updates
    - Timeouts
    
    **Connection Flow:**
    1. Client connects to /ws/supervisor
    2. Server accepts connection
    3. Client receives real-time JSON messages about events
    4. Client disconnects when done
    
    **Message Types:**
    - new_request: New help request created
    - request_resolved: Help request was answered
    - request_timeout: Help request timed out
    - knowledge_base_updated: Knowledge base entry added
    """
    await connection_manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive
            # Client sends ping/pong frames or we receive reconnection heartbeats
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WEBSOCKET ERROR] {e}")
        connection_manager.disconnect(websocket)
