from datetime import datetime, timezone
import uuid

def generate_uuid() -> str:
    """
    Generates a unique, random string UUID4.
    """
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    """
    Returns the current timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)

def format_iso_datetime(dt: datetime) -> str:
    """
    Formats a datetime object to an ISO 8601 string.
    """
    return dt.isoformat()
