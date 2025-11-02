"""
Help Requests API Routes
Handles creation, retrieval, and answering of help requests.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.models.firebase_models import (
    HelpRequestResponse, HelpRequestAnswer
)
from app.services.firebase_service import FirebaseService
from app.services.notification_service import notification_service
from app.database import get_db_ref

router = APIRouter(prefix="/api/help-requests", tags=["help-requests"])

# ======================== Request Models ========================

class HelpRequestCreate(BaseModel):
    """Model for creating a help request"""
    question: str
    caller_info: str = "Anonymous"
    session_id: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Do you have evening appointments?",
                "caller_info": "+1 (555) 123-4567",
                "session_id": "room-123"
            }
        }

# ======================== GET Endpoints ========================

@router.get("", response_model=list[HelpRequestResponse], include_in_schema=False)
@router.get("/", response_model=list[HelpRequestResponse])
async def get_help_requests():
    """
    Get all help requests.
    
    Returns all requests regardless of status (pending, resolved, timeout).
    """
    try:
        requests = await FirebaseService.get_all_help_requests()
        print(f"✅ Retrieved {len(requests)} help requests")
        return requests
    except Exception as e:
        print(f"❌ Error fetching help requests: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching requests: {str(e)}")

@router.get("/{request_id}", response_model=HelpRequestResponse)
async def get_help_request(request_id: str):
    """
    Get a specific help request by ID.
    
    Args:
        request_id: Help request ID
        
    Returns:
        HelpRequestResponse: The help request
    """
    try:
        result = await FirebaseService.get_request_by_id(request_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Request {request_id} not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_stats():
    """
    Get help request statistics.
    
    Returns:
        dict: Statistics with pending, resolved, timeout, and total counts
    """
    try:
        stats = await FirebaseService.get_stats()
        print(f"📊 Stats: Pending={stats['pending']}, Resolved={stats['resolved']}, "
              f"Timeout={stats['timeout']}, Total={stats['total']}")
        return stats
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================== POST Endpoint ========================

@router.post("/", response_model=HelpRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_help_request(request: HelpRequestCreate):
    """
    Create a new help request from agent escalation.
    
    This endpoint is called when the AI agent escalates a question it cannot answer
    to a human supervisor.
    
    Args:
        request: HelpRequestCreate with question, caller_info, and session_id
        
    Returns:
        HelpRequestResponse: The created help request
    """
    try:
        print(f"\n📋 Creating help request...")
        print(f"   Question: {request.question[:50] if len(request.question) > 50 else request.question}...")
        print(f"   Caller: {request.caller_info}")
        print(f"   Session: {request.session_id}")
        
        # Call the service method - it returns HelpRequestResponse
        result = await FirebaseService.create_help_request(
            question=request.question,
            caller_info=request.caller_info,
            session_id=request.session_id
        )
        
        # Notify all connected supervisors about the new request
        try:
            await notification_service.notify_new_request(result)
        except Exception as e:
            print(f"⚠️ Warning: Failed to notify about new request: {e}")
        
        print(f"✅ Help request created successfully")
        print(f"   ID: {result.id}")
        print(f"📢 Broadcasting notification to supervisors\n")
        
        # Return the HelpRequestResponse object directly
        return result
    
    except Exception as e:
        print(f"❌ Error creating help request: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating request: {str(e)}")

# ======================== PUT Endpoint ========================

@router.put("/{request_id}/answer", response_model=HelpRequestResponse)
async def answer_help_request(
    request_id: str,
    answer: str,
    supervisor_name: str
):
    """
    Answer a help request.
    
    When a supervisor provides an answer to a pending help request,
    this endpoint:
    1. Updates the help request with the answer
    2. Marks it as resolved
    3. Automatically adds the Q&A pair to the knowledge base
    4. Notifies the agent about the update
    
    Args:
        request_id: ID of the help request to answer
        answer: The supervisor's answer
        supervisor_name: Name of the supervisor providing the answer
        
    Returns:
        HelpRequestResponse: The updated help request
    """
    try:
        print(f"\n💬 Answering help request...")
        print(f"   ID: {request_id}")
        print(f"   Supervisor: {supervisor_name}")
        print(f"   Answer: {answer[:50] if len(answer) > 50 else answer}...")
        
        # Create answer model
        answer_data = HelpRequestAnswer(
            answer=answer,
            supervisor_name=supervisor_name
        )
        
        # Update the request with the answer
        result = await FirebaseService.answer_request(request_id, answer_data)

        # Notify supervisors about the update
        try:
            await notification_service.notify_request_resolved(result.model_dump())
        except Exception as e:
            print(f"⚠️ Warning: Failed to notify supervisors about answered request: {e}")

        # Notify the customer about the answer (simulated via console log)
        try:
            await notification_service.notify_customer_callback(result.model_dump())
        except Exception as e:
            print(f"⚠️ Warning: Failed to notify customer about answer: {e}")

        print(f"✅ Request answered and knowledge base updated\n")

        return result
    
    except Exception as e:
        print(f"❌ Error answering request: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error answering request: {str(e)}")

# ======================== DELETE Endpoint (Optional) ========================

@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_help_request(request_id: str):
    """
    Delete a help request (optional).
    
    Args:
        request_id: ID of the request to delete
    """
    try:
        ref = get_db_ref(f"/help_requests/{request_id}")
        ref.delete()
        print(f"🗑️ Request deleted: {request_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
