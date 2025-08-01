from markupsafe import escape
import datetime
import re

# Default maximum length for sanitized strings
MAX_STR_LEN = 1024

def sanitize_id(id_value: str) -> int:
    """Convert id parameter to int, raising BadRequest if invalid."""
    intValue = int(id_value)

    if (intValue < 0):
        raise ValueError("ID numbers must be positive integers")
    
    return intValue


def sanitize_str(value: str, max_length: int = MAX_STR_LEN) -> str:
    """Validate and sanitize a string value.

    This helper escapes HTML to mitigate HTML/JS injection attempts,
    removes a few characters commonly used in SQL injections and
    enforces a length limit to avoid overflow attacks.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid input type")
    if len(value) > max_length:
        raise ValueError("Input too long")

    # Escape HTML first to neutralize script tags
    escaped_value = escape(value)

    # Remove characters frequently used for SQL/JS injection
    cleaned_value = re.sub(r"[\"';`]|--", "", escaped_value)

    return cleaned_value


def sanitize_datetime(value: str) -> datetime.datetime:
    """Parse ISO formatted datetime string."""
    if not isinstance(value, str):
        raise ValueError("Invalid datetime format")
    
    return datetime.datetime.fromisoformat(value)
