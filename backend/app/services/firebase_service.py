"""
Firebase Service for Realtime Database operations.
Handles help requests, knowledge base, and statistics.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
from uuid import uuid4

from app.database import get_db_ref
from app.models.firebase_models import (
    HelpRequest, HelpRequestCreate, HelpRequestAnswer,
    HelpRequestResponse, KnowledgeBaseEntry, KnowledgeBaseResponse,
    RequestStatus, KnowledgeSource
)


class FirebaseService:
    """Service for Firebase Realtime Database operations"""
    
    # ======================== Help Requests ========================
    
    @staticmethod
    async def create_help_request(
        question: str,
        caller_info: str = "Anonymous",
        session_id: str = ""
    ) -> HelpRequestResponse:
        """
        Create new help request in Firebase.
        
        FIXED: Now accepts individual parameters instead of HelpRequestCreate object.
        This matches how the agent calls it.
        
        Args:
            question: Customer's question
            caller_info: Customer's name or phone number
            session_id: LiveKit room/session ID
            
        Returns:
            HelpRequestResponse: Created help request
        """
        try:
            request_id = str(uuid4())
            now = datetime.utcnow().isoformat()
            timeout_at = (datetime.utcnow() + timedelta(hours=2)).isoformat()
            
            # Create help request data
            help_request_data = {
                "id": request_id,
                "question": question,
                "caller_info": caller_info or "Anonymous",
                "status": RequestStatus.PENDING.value,
                "created_at": now,
                "resolved_at": None,
                "timeout_at": timeout_at,
                "answer": None,
                "answered_by": None,
                "session_id": session_id,
                "callback_info": json.dumps({
                    "phone": caller_info,
                    "ask_time": now
                }),
                "attempt_count": 0
            }
            
            # Save to Firebase
            ref = get_db_ref(f"/help_requests/{request_id}")
            ref.set(help_request_data)
            
            print(f"✅ Help request created: {request_id}")
            print(f"   Question: {question[:50] if len(question) > 50 else question}...")
            
            return HelpRequestResponse(**help_request_data)
        
        except Exception as e:
            print(f"❌ Error creating help request: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    async def get_pending_requests() -> List[HelpRequestResponse]:
        """
        Get all pending help requests.
        
        Returns:
            List[HelpRequestResponse]: List of pending requests
        """
        try:
            ref = get_db_ref("/help_requests")
            data = ref.get()
        
            if not data or not isinstance(data, dict):
                return []
        
            pending_requests = []
            for request_id, request_data in data.items():
                # Skip the "initialized" marker
                if request_id == "initialized":
                    continue
                
                if isinstance(request_data, dict) and request_data.get("status") == RequestStatus.PENDING.value:
                    try:
                        pending_requests.append(HelpRequestResponse(**request_data))
                    except Exception as e:
                        print(f"⚠️ Error parsing pending request {request_id}: {e}")
                        continue
        
            # Sort by created_at (newest first)
            pending_requests.sort(key=lambda x: x.created_at, reverse=True)
            return pending_requests
        
        except Exception as e:
            print(f"❌ Error getting pending requests: {e}")
            return []
    
    @staticmethod
    async def get_all_help_requests() -> List[HelpRequestResponse]:
        """
        Get all help requests (pending, resolved, timeout).
        
        Returns:
            List[HelpRequestResponse]: All help requests
        """
        try:
            ref = get_db_ref("/help_requests")
            data = ref.get()
        
            if not data or not isinstance(data, dict):
                return []
        
            all_requests = []
            for request_id, request_data in data.items():
                # Skip the "initialized" marker
                if request_id == "initialized":
                    continue
                
                if isinstance(request_data, dict):
                    try:
                        all_requests.append(HelpRequestResponse(**request_data))
                    except Exception as e:
                        print(f"⚠️ Error parsing request {request_id}: {e}")
                        continue
        
            # Sort by created_at (newest first)
            all_requests.sort(key=lambda x: x.created_at, reverse=True)
            return all_requests
        
        except Exception as e:
            print(f"❌ Error getting all help requests: {e}")
            return []
    
    @staticmethod
    async def get_request_by_id(request_id: str) -> Optional[HelpRequestResponse]:
        """
        Get specific help request by ID.
        
        Args:
            request_id: Help request ID
            
        Returns:
            HelpRequestResponse or None if not found
        """
        try:
            ref = get_db_ref(f"/help_requests/{request_id}")
            data = ref.get()
            
            if data:
                return HelpRequestResponse(**data)
            return None
        except Exception as e:
            print(f"❌ Error getting request {request_id}: {e}")
            return None
    
    @staticmethod
    async def answer_request(
        request_id: str,
        answer_data: HelpRequestAnswer
    ) -> HelpRequestResponse:
        """
        Answer a help request and update knowledge base.
        
        Args:
            request_id: Help request ID
            answer_data: Answer from supervisor
            
        Returns:
            HelpRequestResponse: Updated help request
            
        Raises:
            ValueError: If request not found
        """
        try:
            # Get current request
            ref = get_db_ref(f"/help_requests/{request_id}")
            request_data = ref.get()
            
            if not request_data:
                raise ValueError(f"Request {request_id} not found")
            
            # Update request
            request_data["status"] = RequestStatus.RESOLVED.value
            request_data["answer"] = answer_data.answer
            request_data["answered_by"] = answer_data.supervisor_name
            request_data["resolved_at"] = datetime.utcnow().isoformat()
            
            ref.set(request_data)
            
            # Add to knowledge base
            await FirebaseService.add_to_knowledge_base(
                request_data["question"],
                answer_data.answer
            )
            
            print(f"✅ Request answered: {request_id}")
            print(f"   Answer: {answer_data.answer[:50] if len(answer_data.answer) > 50 else answer_data.answer}...")
            
            return HelpRequestResponse(**request_data)
        
        except Exception as e:
            print(f"❌ Error answering request {request_id}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    async def timeout_request(request_id: str) -> HelpRequestResponse:
        """
        Mark request as timed out.
        
        Args:
            request_id: Help request ID
            
        Returns:
            HelpRequestResponse: Updated help request
        """
        try:
            ref = get_db_ref(f"/help_requests/{request_id}")
            request_data = ref.get()
            
            if request_data:
                request_data["status"] = RequestStatus.TIMEOUT.value
                ref.set(request_data)
                print(f"⏱️ Request timed out: {request_id}")
                return HelpRequestResponse(**request_data)
            
            raise ValueError(f"Request {request_id} not found")
        
        except Exception as e:
            print(f"❌ Error timing out request {request_id}: {e}")
            raise
    
    @staticmethod
    async def get_stats() -> dict:
        """
        Get help request statistics.
        
        Returns:
            dict: Statistics with pending, resolved, timeout, total counts
        """
        try:
            ref = get_db_ref("/help_requests")
            data = ref.get()
        
            if not data or not isinstance(data, dict):
                return {"pending": 0, "resolved": 0, "timeout": 0, "total": 0}
        
            pending = sum(
                1 for r in data.values() 
                if isinstance(r, dict) and r.get("status") == RequestStatus.PENDING.value
            )
            resolved = sum(
                1 for r in data.values() 
                if isinstance(r, dict) and r.get("status") == RequestStatus.RESOLVED.value
            )
            timeout = sum(
                1 for r in data.values() 
                if isinstance(r, dict) and r.get("status") == RequestStatus.TIMEOUT.value
            )
        
            return {
                "pending": pending,
                "resolved": resolved,
                "timeout": timeout,
                "total": pending + resolved + timeout
            }
        
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {"pending": 0, "resolved": 0, "timeout": 0, "total": 0}
    
    # ======================== Knowledge Base ========================
    
    @staticmethod
    async def add_to_knowledge_base(question: str, answer: str) -> KnowledgeBaseResponse:
        """
        Add new entry to knowledge base.
        
        Args:
            question: Question
            answer: Answer
            
        Returns:
            KnowledgeBaseResponse: Created knowledge base entry
        """
        try:
            kb_id = str(uuid4())
            now = datetime.utcnow().isoformat()
            
            kb_entry_data = {
                "id": kb_id,
                "question": question,
                "answer": answer,
                "source": KnowledgeSource.LEARNED.value,
                "created_at": now,
                "updated_at": now,
                "use_count": 0
            }
            
            ref = get_db_ref(f"/knowledge_base/{kb_id}")
            ref.set(kb_entry_data)
            
            print(f"📚 Added to knowledge base: {kb_id}")
            print(f"   Q: {question[:50] if len(question) > 50 else question}...")
            print(f"   A: {answer[:50] if len(answer) > 50 else answer}...")
            
            return KnowledgeBaseResponse(**kb_entry_data)
        
        except Exception as e:
            print(f"❌ Error adding to knowledge base: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    async def get_all_kb_entries() -> List[KnowledgeBaseResponse]:
        """
        Get all knowledge base entries.
        
        Returns:
            List[KnowledgeBaseResponse]: All knowledge base entries
        """
        try:
            ref = get_db_ref("/knowledge_base")
            data = ref.get()
        
            if not data or not isinstance(data, dict):
                return []
        
            entries = []
            for entry_id, entry_data in data.items():
                if entry_id == "initialized":
                    continue
            
                if isinstance(entry_data, dict):
                    try:
                        entries.append(KnowledgeBaseResponse(**entry_data))
                    except Exception as e:
                        print(f"⚠️ Error parsing KB entry {entry_id}: {e}")
                        continue
        
            entries.sort(key=lambda x: x.updated_at, reverse=True)
            return entries
        
        except Exception as e:
            print(f"❌ Error getting KB entries: {e}")
            return []
    
    @staticmethod
    async def create_kb_entry(question: str, answer: str) -> KnowledgeBaseResponse:
        """
        Create manual knowledge base entry.
        
        Args:
            question: Question
            answer: Answer
            
        Returns:
            KnowledgeBaseResponse: Created knowledge base entry
        """
        try:
            kb_id = str(uuid4())
            now = datetime.utcnow().isoformat()
            
            kb_entry_data = {
                "id": kb_id,
                "question": question,
                "answer": answer,
                "source": KnowledgeSource.MANUAL.value,
                "created_at": now,
                "updated_at": now,
                "use_count": 0
            }
            
            ref = get_db_ref(f"/knowledge_base/{kb_id}")
            ref.set(kb_entry_data)
            
            print(f"📝 Manual KB entry created: {kb_id}")
            
            return KnowledgeBaseResponse(**kb_entry_data)
        
        except Exception as e:
            print(f"❌ Error creating KB entry: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    @staticmethod
    async def get_kb_as_dict() -> dict:
        """
        Export knowledge base as dictionary for agent.
        
        Returns:
            dict: Dictionary with question keys and answer values
        """
        try:
            ref = get_db_ref("/knowledge_base")
            data = ref.get() or {}
            
            kb_dict = {}
            for entry_id, entry in data.items():
                if isinstance(entry, dict) and "question" in entry and "answer" in entry:
                    key = entry.get("question", "")[:50].lower().replace(" ", "_")
                    kb_dict[key] = entry.get("answer", "")
            
            return kb_dict
        
        except Exception as e:
            print(f"❌ Error exporting KB: {e}")
            return {}
    
    @staticmethod
    async def increment_kb_use_count(kb_id: str):
        """
        Increment use count for knowledge base entry.
        
        Args:
            kb_id: Knowledge base entry ID
        """
        try:
            ref = get_db_ref(f"/knowledge_base/{kb_id}")
            entry = ref.get()
            
            if entry:
                entry["use_count"] = entry.get("use_count", 0) + 1
                entry["updated_at"] = datetime.utcnow().isoformat()
                ref.set(entry)
                print(f"📊 KB use count incremented: {kb_id}")
        
        except Exception as e:
            print(f"❌ Error incrementing KB use count: {e}")
