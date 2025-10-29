import uuid
from database import serialize_document
from datetime import datetime, timezone
from typing import Optional
import pytz
from zoneinfo import ZoneInfo

def generate_unique_id(prefix: str) -> str:
    """Generate a unique ID with a prefix"""
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

def format_datetime(dt_str: str) -> str:
    """Validate and format datetime string"""
    try:
        # Try to parse the date to ensure it's valid
        datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt_str
    except ValueError:
        raise ValueError("Invalid datetime format. Expected ISO format (YYYY-MM-DDTHH:MM:SS)")



def get_current_utc():
    """Get current UTC time"""
    return datetime.now(timezone.utc)

def get_datetime() -> str:
    """Get current UTC+5:45 time in ISO format (string)."""
    nepal_timezone = pytz.timezone('Asia/Kathmandu')
    return datetime.now(nepal_timezone).isoformat()