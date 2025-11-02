"""Helper utility functions"""
from datetime import datetime
from typing import Dict, Any
import json

def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO format string"""
    if isinstance(dt, str):
        return dt
    return dt.isoformat()

def parse_timestamp(ts: str) -> datetime:
    """Parse ISO format string to datetime"""
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts)

def dict_to_json(data: Dict[str, Any]) -> str:
    """Convert dictionary to JSON string"""
    return json.dumps(data, default=str)

def json_to_dict(data: str) -> Dict[str, Any]:
    """Convert JSON string to dictionary"""
    return json.loads(data)

def truncate_string(text: str, length: int = 100) -> str:
    """Truncate string to specified length with ellipsis"""
    if len(text) > length:
        return text[:length] + "..."
    return text

def log_request(request_id: str, action: str, details: str = ""):
    """Log a request action"""
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] Request {request_id}: {action} {details}")
