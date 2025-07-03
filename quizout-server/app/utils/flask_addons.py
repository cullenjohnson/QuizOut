import functools
from flask import request
from flask_login import current_user
from flask_socketio import disconnect, emit

def authenticated_only(f):
    """Custom wrapper to for socketio events to disconnect clients if they aren't authenticated."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped