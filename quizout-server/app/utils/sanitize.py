from markupsafe import escape
from werkzeug.exceptions import BadRequest
import datetime

def sanitize_id(id_value: str) -> int:
    """Convert id parameter to int, raising BadRequest if invalid."""
    try:
        return int(id_value)
    except (TypeError, ValueError):
        raise BadRequest("Invalid id parameter")


def sanitize_str(value: str) -> str:
    """Escape string inputs to avoid injection."""
    if not isinstance(value, str):
        raise BadRequest("Invalid input type")
    return escape(value)


def sanitize_datetime(value: str) -> datetime.datetime:
    """Parse ISO formatted datetime string."""
    if not isinstance(value, str):
        raise BadRequest("Invalid datetime format")
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        raise BadRequest("Invalid datetime format")
