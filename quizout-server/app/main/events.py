import json
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

@socketio.event
def playerBuzzed(playerName:str):
    logger.debug(f'Client [sid {request.sid}] says player buzzed: {playerName}.')
    socketio.emit('playerAnswering', playerName)

@socketio.on('resetBuzzers')
@authenticated_only
def resetBuzzers(dataJson):
    logger.debug(f'Client [sid {request.sid}] reset the buzzers. {dataJson}')
    socketio.emit('resetBuzzers', dataJson)

@socketio.on('buzzerTimeout')
@authenticated_only
def buzzerTimeout():
    logger.debug(f'Client [sid {request.sid}] timed out the buzzers.')
    socketio.emit('buzzerTimeout')

@socketio.on('playerCorrect')
@authenticated_only
def playerCorrect(playerKey):
    logger.debug(f'Client [sid {request.sid}] said player {playerKey} was corrrect.')
    socketio.emit('playerCorrect', playerKey)

@socketio.on('playerIncorrect')
@authenticated_only
def playerIncorrect(playerKey):
    logger.debug(f'Client [sid {request.sid}] said player {playerKey} was incorrect.')
    socketio.emit('playerIncorrect', playerKey)