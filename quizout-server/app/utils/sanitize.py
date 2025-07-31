from markupsafe import escape
from werkzeug.exceptions import BadRequest
import datetime
import re

# Default maximum length for sanitized strings
MAX_STR_LEN = 1024

def sanitize_id(id_value: str) -> int:
    """Convert id parameter to int, raising BadRequest if invalid."""
    try:
        return int(id_value)
    except (TypeError, ValueError):
        raise BadRequest("Invalid id parameter")


def sanitize_str(value: str, max_length: int = MAX_STR_LEN) -> str:
    """Validate and sanitize a string value.

    This helper escapes HTML to mitigate HTML/JS injection attempts,
    removes a few characters commonly used in SQL injections and
    enforces a length limit to avoid overflow attacks.
    """
    if not isinstance(value, str):
        raise BadRequest("Invalid input type")
    if len(value) > max_length:
        raise BadRequest("Input too long")

    # Escape HTML first to neutralize script tags
    escaped_value = escape(value)

    # Remove characters frequently used for SQL/JS injection
    cleaned_value = re.sub(r"[\"';`]|--", "", escaped_value)

    return cleaned_value


def sanitize_datetime(value: str) -> datetime.datetime:
    """Parse ISO formatted datetime string."""
    if not isinstance(value, str):
        raise BadRequest("Invalid datetime format")
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        raise BadRequest("Invalid datetime format")
