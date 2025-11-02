import asyncio
from datetime import datetime
from app.database import get_db_ref
from app.models.firebase_models import RequestStatus

class TimeoutService:
    """Service for checking and handling timed-out help requests"""
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
        self.running = False
    
    async def start(self):
        """Start the timeout checker background task"""
        self.running = True
        asyncio.create_task(self._check_timeouts_loop())
        print("[TIMEOUT SERVICE] ⏱️ Started - checking every 5 minutes")
    
    async def stop(self):
        """Stop the timeout checker"""
        self.running = False
        print("[TIMEOUT SERVICE] 🛑 Stopped")
    
    async def _check_timeouts_loop(self):
        """Periodically check for timed-out requests"""
        while self.running:
            try:
                await self._process_timeouts()
                # Check every 5 minutes
                await asyncio.sleep(300)
            except Exception as e:
                print(f"[TIMEOUT SERVICE ERROR] {e}")
                await asyncio.sleep(60)
    
    async def _process_timeouts(self):
        """Find and timeout expired requests"""
        now = datetime.utcnow()
        
        try:
            # Get all pending requests from Firebase
            ref = get_db_ref("/help_requests")
            data = ref.get()  # FIXED: Removed .val()
            
            if not data or not isinstance(data, dict):
                return  # No data to process
            
            timed_out_requests = []
            
            for request_id, request_data in data.items():
                # Skip non-dict entries and the initialized marker
                if not isinstance(request_data, dict) or request_id == "initialized":
                    continue
                
                if request_data.get("status") == RequestStatus.PENDING.value:
                    try:
                        timeout_at = datetime.fromisoformat(request_data.get("timeout_at"))
                        if timeout_at <= now:
                            timed_out_requests.append((request_id, request_data))
                    except (ValueError, TypeError) as e:
                        print(f"[TIMEOUT SERVICE] Error parsing date for {request_id}: {e}")
            
            if timed_out_requests:
                print(f"[TIMEOUT SERVICE] ⏱️ Found {len(timed_out_requests)} timed-out request(s)")
                
                for request_id, request_data in timed_out_requests:
                    request_data["status"] = RequestStatus.TIMEOUT.value
                    ref.child(request_id).set(request_data)
                    
                    # Notify supervisor
                    await self.notification_service.notify_request_timeout(request_data)
                    
                    # Log follow-up message
                    print(f"\n[CUSTOMER NOTIFICATION - TIMEOUT]")
                    print(f"To: {request_data.get('caller_info', 'Unknown')}")
                    print(f"Question: {request_data.get('question')}")
                    print(f"Message: Your question is taking longer than expected.")
                    print(f"[End Notification]\n")
        
        except Exception as e:
            # Silently handle errors in timeout service to prevent crashes
            print(f"[TIMEOUT SERVICE] Error in _process_timeouts: {e}")
