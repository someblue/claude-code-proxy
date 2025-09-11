"""
Request context management for tracking current API key.
"""

import contextvars
from typing import Optional

# Context variable to store the current API key for the request
current_api_key: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'current_api_key', default=None
)

def set_current_api_key(api_key: str) -> None:
    """Set the current API key for the request context."""
    current_api_key.set(api_key)

def get_current_api_key() -> Optional[str]:
    """Get the current API key from the request context."""
    return current_api_key.get()