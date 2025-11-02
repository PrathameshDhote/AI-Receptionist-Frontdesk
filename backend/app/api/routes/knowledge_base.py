from fastapi import APIRouter, HTTPException, status

from app.models.firebase_models import KnowledgeBaseResponse
from app.services.firebase_service import FirebaseService
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge-base"])

@router.get(
    "/",
    response_model=list[KnowledgeBaseResponse],
    summary="Get All Entries",
    description="Get all knowledge base entries"
)
async def get_knowledge_base():
    """
    Get all knowledge base entries.
    
    Returns the complete knowledge base sorted by most recently updated entries first.
    
    **Returns:** List of all knowledge base entries
    """
    try:
        return await FirebaseService.get_all_kb_entries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch knowledge base: {str(e)}")

@router.post(
    "/",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Entry",
    description="Create new knowledge base entry"
)
async def create_kb_entry(question: str, answer: str):
    """
    Create a new knowledge base entry.
    
    **Query Parameters:**
    - question: The question
    - answer: The answer
    
    **Returns:** The created knowledge base entry
    """
    try:
        if not question or not answer:
            raise HTTPException(status_code=400, detail="Question and answer are required")
        
        result = await FirebaseService.create_kb_entry(question, answer)
        
        await notification_service.notify_kb_updated(question, answer)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

@router.get(
    "/{kb_id}",
    response_model=KnowledgeBaseResponse,
    summary="Get Specific Entry",
    description="Get a specific knowledge base entry by ID"
)
async def get_kb_entry(kb_id: str):
    """
    Get a specific knowledge base entry by ID.
    
    **Parameters:**
    - kb_id: The ID of the knowledge base entry
    
    **Returns:** The knowledge base entry
    **Raises:** 404 if entry not found
    """
    try:
        entries = await FirebaseService.get_all_kb_entries()
        for entry in entries:
            if entry.id == kb_id:
                return entry
        raise HTTPException(status_code=404, detail=f"Entry {kb_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/dump/dict",
    response_model=dict,
    summary="Export as Dictionary",
    description="Export knowledge base as dictionary (for agent)"
)
async def get_kb_as_dict():
    """
    Export knowledge base as a dictionary.
    
    This endpoint is used by the LiveKit agent to get the knowledge base
    in a format optimized for inclusion in the LLM system prompt.
    
    **Returns:** Dictionary with question keys and answer values
    """
    try:
        return await FirebaseService.get_kb_as_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export KB: {str(e)}")
