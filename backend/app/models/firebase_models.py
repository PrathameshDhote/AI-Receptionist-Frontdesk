from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from enum import Enum

# ======================== Enums ========================

class RequestStatus(str, Enum):
    """Status of help requests"""
    PENDING = "pending"
    RESOLVED = "resolved"
    TIMEOUT = "timeout"

class KnowledgeSource(str, Enum):
    """Source of knowledge base entries"""
    INITIAL = "initial"
    LEARNED = "learned"
    MANUAL = "manual"

# ======================== Help Request Models ========================

class HelpRequestCreate(BaseModel):
    """Request body for creating help request"""
    question: str = Field(..., min_length=5, max_length=500, description="Customer's question")
    caller_info: Optional[str] = Field(None, max_length=255, description="Customer name or phone")
    session_id: str = Field(..., max_length=255, description="LiveKit room/session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Do you have evening appointments available?",
                "caller_info": "+1 (555) 123-4567",
                "session_id": "room-123"
            }
        }

class HelpRequestAnswer(BaseModel):
    """Request body for answering help request"""
    answer: str = Field(..., min_length=5, max_length=2000, description="Supervisor's answer")
    supervisor_name: str = Field(..., max_length=100, description="Supervisor's name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Yes, we're open until 9 PM on weekdays and 6 PM on weekends.",
                "supervisor_name": "Sarah"
            }
        }

class HelpRequest(BaseModel):
    """Help Request model - stored in Firebase at /help_requests/{id}"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str = Field(..., description="Customer's question")
    caller_info: Optional[str] = None
    status: RequestStatus = RequestStatus.PENDING
    
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None
    timeout_at: str
    
    answer: Optional[str] = None
    answered_by: Optional[str] = None
    
    session_id: str
    callback_info: Optional[str] = None
    attempt_count: int = 0
    
    class Config:
        from_attributes = True

class HelpRequestResponse(BaseModel):
    """Response model for help requests"""
    id: str
    question: str
    caller_info: Optional[str] = None
    status: str
    created_at: str
    resolved_at: Optional[str] = None
    timeout_at: str
    answer: Optional[str] = None
    answered_by: Optional[str] = None
    session_id: str

# ======================== Knowledge Base Models ========================

class KnowledgeBaseEntry(BaseModel):
    """Knowledge Base Entry - stored in Firebase at /knowledge_base/{id}"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str = Field(..., description="Question")
    answer: str = Field(..., description="Answer")
    source: KnowledgeSource = KnowledgeSource.MANUAL
    
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    use_count: int = 0
    
    class Config:
        from_attributes = True

class KnowledgeBaseResponse(BaseModel):
    """Response model for knowledge base"""
    id: str
    question: str
    answer: str
    source: str
    created_at: str
    updated_at: str
    use_count: int
