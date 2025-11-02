from typing import List, Dict, Any
import json
from datetime import datetime

class ConnectionManager:
    """Manage WebSocket connections for real-time notifications"""
    
    def __init__(self):
        self.active_connections: List = []
    
    async def connect(self, websocket):
        """Accept and track new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WEBSOCKET] ✅ Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WEBSOCKET] 🔌 Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected supervisors.
        
        Args:
            message: Dictionary message to send
        """
        if not self.active_connections:
            print("[WEBSOCKET] ℹ️ No active connections to broadcast to")
            return
        
        failed_connections = []
        
        for i, connection in enumerate(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WEBSOCKET ERROR] Failed to send message to client {i}: {e}")
                failed_connections.append(connection)
        
        # Clean up failed connections
        for conn in failed_connections:
            self.disconnect(conn)

class NotificationService:
    """Service for sending real-time notifications to supervisors"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def notify_new_request(self, request_data: Dict[str, Any]):
        """
        Notify supervisors of new help request.
        
        Args:
            request_data: Help request data
        """
        message = {
            "type": "new_request",
            "data": {
                "request_id": request_data.get("id"),
                "question": request_data.get("question"),
                "caller_info": request_data.get("caller_info"),
                "created_at": request_data.get("created_at"),
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"📢 Broadcasting new request notification")
        await self.manager.broadcast(message)
    
    async def notify_request_resolved(self, request_data: Dict[str, Any]):
        """
        Notify supervisors that request was resolved.

        Args:
            request_data: Help request data
        """
        message = {
            "type": "request_resolved",
            "data": {
                "request_id": request_data.get("id"),
                "answer": request_data.get("answer"),
                "answered_by": request_data.get("answered_by"),
                "resolved_at": request_data.get("resolved_at")
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        print(f"✅ Broadcasting request resolved notification")
        await self.manager.broadcast(message)

    async def notify_customer_callback(self, request_data: Dict[str, Any]):
        """
        Simulate sending a text message to the customer when supervisor answers.

        This simulates the callback mechanism to notify the customer that their
        question has been answered by the supervisor.

        In production, this would:
        - Send an SMS via Twilio/similar service
        - Make a webhook call to the telephony system
        - Trigger a push notification

        For this local demo, we log the notification to console.

        Args:
            request_data: Help request data with answer
        """
        caller_info = request_data.get("caller_info", "Anonymous")
        question = request_data.get("question", "")
        answer = request_data.get("answer", "")
        answered_by = request_data.get("answered_by", "Supervisor")

        # Simulate SMS/text callback to customer
        print("\n" + "="*70)
        print("📱 CUSTOMER NOTIFICATION ")
        print("="*70)
        print(f"To: {caller_info}")
        print(f"From: Beautiful Hair Salon")
        print(f"Time: {datetime.utcnow().isoformat()}")
        print()
        print(f"Message:")
        print(f"  Hi! Thanks for calling Beautiful Hair Salon.")
        print(f"  Your question: \"{question[:60]}{'...' if len(question) > 60 else ''}\"")
        print()
        print(f"  Our {answered_by} has answered:")
        print(f"  \"{answer[:100]}{'...' if len(answer) > 100 else ''}\"")
        print()
        print(f"  Feel free to call us again if you have more questions!")
        print("="*70 + "\n")

        # In production, you would do:
        # await send_sms(to=caller_info, message=formatted_message)
        # or
        # await webhook_call(url=callback_url, data=notification_data)
    
    async def notify_request_timeout(self, request_data: Dict[str, Any]):
        """
        Notify supervisors of timed-out request.
        
        Args:
            request_data: Help request data
        """
        message = {
            "type": "request_timeout",
            "data": {
                "request_id": request_data.get("id"),
                "question": request_data.get("question"),
                "created_at": request_data.get("created_at"),
                "caller_info": request_data.get("caller_info")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"⏱️ Broadcasting request timeout notification")
        await self.manager.broadcast(message)
    
    async def notify_kb_updated(self, question: str, answer: str):
        """
        Notify supervisors of knowledge base update.
        
        Args:
            question: Knowledge base question
            answer: Knowledge base answer
        """
        message = {
            "type": "knowledge_base_updated",
            "data": {
                "question": question,
                "answer": answer
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"📚 Broadcasting KB updated notification")
        await self.manager.broadcast(message)

# Global instance
connection_manager = ConnectionManager()
notification_service = NotificationService(connection_manager)
