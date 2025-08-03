import jsonpickle
import uuid
from flask_socketio import emit, join_room, leave_room
from flask import request

from .. import socketio, db
from ..sharedLogger import logger
from ..utils.flask_addons import authenticated_only
from ..models import BuzzerClient

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


@socketio.event
def buzzerClientConnected(clientInfoStr):
    clientInfo = jsonpickle.decode(clientInfoStr, classes=(uuid.UUID))
    logger.info(f'Client [sid {request.sid}] sent buzzer session info: {str(clientInfo)}')

    buzzerClient = BuzzerClient(
        uuid = uuid.UUID(clientInfo['uuid']['hex']),
        ip = clientInfo['ip'],
        teamBuzzerInfo = clientInfo['teamBuzzerInfo'])
    
    db.session.add(buzzerClient)
    db.session.commit()

    socketio.emit('updateBuzzerClient', jsonpickle.encode(buzzerClient.serialize(), unpicklable=False))

@socketio.on('adminClientConnected')
@authenticated_only
def adminClientConnected():
    logger.debug(f'Admin client [sid {request.sid}] connected')
    
    lastBuzzerClient = BuzzerClient.query.order_by(BuzzerClient.id.desc()).first()

    if lastBuzzerClient is not None:
        socketio.emit('updateBuzzerClient', jsonpickle.encode(lastBuzzerClient.serialize(), unpicklable=False))


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

@socketio.event
def buzzersListening(data):
    logger.info(f'Client [sid {request.sid}] said buzzers are listening. {data}')
    socketio.emit('buzzersListening', data)

@socketio.event
def buzzersCanceled(data):
    logger.info(f'Client [sid {request.sid}] said buzzers canceled: {data}')
    socketio.emit('buzzersCanceled', data)