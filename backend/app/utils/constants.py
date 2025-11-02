from enum import Enum
from typing import Dict

class RequestStatus(str, Enum):
    """Request status enumeration"""
    PENDING = "pending"
    RESOLVED = "resolved"
    TIMEOUT = "timeout"

class KnowledgeSource(str, Enum):
    """Knowledge source enumeration"""
    INITIAL = "initial"
    LEARNED = "learned"
    MANUAL = "manual"

REQUEST_STATUSES: Dict[str, str] = {
    "pending": "Waiting for supervisor response",
    "resolved": "Question answered and communicated to customer",
    "timeout": "Supervisor did not respond within timeout period"
}

INITIAL_KNOWLEDGE_BASE = {
    "hours": "Monday-Saturday 9 AM to 7 PM, Sunday 10 AM to 5 PM",
    "services": "Hair cutting, coloring, styling, treatments, extensions, perms",
    "prices": "Haircuts from $45, coloring from $85, styling from $35, treatments from $25",
    "location": "123 Beauty Lane, Downtown District, City",
    "phone": "(555) 123-4567",
    "website": "beautyhairsalon.com",
    "booking": "Book online at beautyhairsalon.com or call us",
    "parking": "Free parking available in building lot",
    "walk_ins": "Walk-ins welcome, but appointments recommended"
}

SYSTEM_INSTRUCTIONS = """You are a friendly AI receptionist for Beautiful Hair Salon.

Your job is to help customers with questions about:
- Operating hours
- Available services
- Pricing
- Location and directions
- Booking appointments

If you don't know the answer, use the request_help function to escalate to a human supervisor.

Be polite, professional, and helpful. Keep responses concise."""
