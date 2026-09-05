from datetime import datetime, timezone
from typing import Optional

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

def format_iso(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    return dt.isoformat()

def get_relative_time(dt: Optional[datetime]) -> str:
    if not dt:
        return "Not specified"
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    seconds = int(diff.total_seconds())
    if seconds < 0:
        return "Just now"
    if seconds < 60:
        return f"{seconds}s ago"
    
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
        
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
        
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
        
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
        
    return "Possibly outdated"
