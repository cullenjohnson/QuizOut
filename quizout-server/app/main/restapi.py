from flask import request
from flask_login import login_required, current_user
from werkzeug.exceptions import Unauthorized
import datetime

from . import restapi_blueprint as restapi
from .. import db
from ..models import User, Player

@restapi.get('/players')
@login_required
def getPlayers():
    players = Player.query \
        .filter_by(created_by=current_user) \
        .order_by(Player.last_played.desc())

    return [player.serialize() for player in players]

@restapi.get('/players/<id>')
@login_required
def getPlayer(id):
    player = db.session.get(Player, id)
    if player.created_by != current_user:
        raise Unauthorized("You are not authorized to view this resource.")
    
    return player.serialize()

@restapi.post('/players')
@login_required
def createPlayer():
    playerJson = request.get_json()

    new_player = Player(name=playerJson['name'], created_by=current_user, last_played=datetime.datetime.now(datetime.UTC))
    db.session.add(new_player)
    db.session.commit()

    return new_player.serialize()

@restapi.put('/players/<int:id>')
@login_required
def updatePlayer(id):
    player = db.session.get(Player, id)
    if player.created_by != current_user:
        raise Unauthorized("You are not authorized to update this resource.")
    
    playerJson = request.get_json()
    player.last_played = datetime.datetime.fromisoformat(playerJson['last_played'])

    db.session.commit()

    return player.serialize()

@restapi.delete('/players/<int:id>')
@login_required
def deletePlayer(id):
    player = db.session.get(Player, id)
    if player.created_by != current_user:
        raise Unauthorized("You are not authorized to delete this resource.")
    
    db.session.delete(player)
    db.session.commit()

    return ('', 204)