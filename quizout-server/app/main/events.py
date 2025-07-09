from flask_socketio import emit, join_room, leave_room
from flask import request
from .. import socketio
from ..sharedLogger import logger
from ..utils.flask_addons import authenticated_only

@socketio.event
def connect(data = None):
    if data:
        logger.info(f'Client [sid {request.sid}] connected with data:', data)
    else:
        logger.info(f'Client [sid {request.sid}] connected')
    emit('response', 'Welcome to the QuizOut server!')

@socketio.event
def message(data = None):
    logger.debug(f'Client [sid {request.sid}] sent message:{data}.')
    socketio.emit('response', f'Server received message: {data}')

@socketio.on('resetBuzzers')
@authenticated_only
def resetBuzzers():
    logger.debug(f'Client [sid {request.sid}] reset the buzzers.')
    socketio.emit('resetBuzzers')