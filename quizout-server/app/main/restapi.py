from flask import request
from flask_login import login_required, current_user
from werkzeug.exceptions import HTTPException, Unauthorized, BadRequest, NotFound
import datetime

from ..utils.sanitize import sanitize_id, sanitize_str, sanitize_datetime
from ..utils import json_error_handler
from . import restapi_blueprint as restapi
from .. import db
from ..models import User, Player

@restapi.errorhandler(HTTPException)
def handleError(e):
    return json_error_handler(e)

@restapi.get('/players')
@login_required
def getPlayers():
    players = Player.query \
        .filter_by(created_by=current_user) \
        .order_by(Player.name.asc())

    return [player.serialize() for player in players]

@restapi.get('/players/<id>')
@login_required
def getPlayer(id):
    player_id = None

    try:
        player_id = sanitize_id(id)
    except (ValueError, TypeError) as e:
        raise BadRequest(f"Invalid Player ID: {e}")
    
    player = db.session.get(Player, player_id)

    if player is None:
        raise NotFound("Player not found.")

    if player.created_by != current_user:
        raise Unauthorized("You are not authorized to view this resource.")

    return player.serialize()

@restapi.post('/players')
@login_required
def createOrUpdatePlayer():
    playerJson = request.get_json()

    name = ""
    try:
        name = sanitize_str(playerJson.get('name'), 200)
    except (ValueError, TypeError) as e:
        raise BadRequest(f"Invalid Player Name: {e}")
    
    player = Player.query.filter_by(name=name, created_by=current_user).scalar()

    if player is not None:
        # If there is already a player of the same name for this user, update the last_played time.
        player.last_played=datetime.datetime.now(datetime.UTC)

    else:
        player = Player(name=name, created_by=current_user, last_played=datetime.datetime.now(datetime.UTC))
        db.session.add(player)

    db.session.commit()

    return player.serialize()

@restapi.put('/players/<int:id>')
@login_required
def updatePlayer(id):
    player_id = None

    try:
        player_id = sanitize_id(id)
    except (ValueError, TypeError) as e:
        raise BadRequest(f"Invalid Player ID: {e}")
    
    player = db.session.get(Player, player_id)

    if player is None:
        raise NotFound("Player not found.")

    if player.created_by != current_user:
        raise Unauthorized("You are not authorized to update this resource.")

    playerJson = request.get_json()

    try:
        player.last_played = sanitize_datetime(playerJson['last_played'])
    except (ValueError, TypeError) as e:
        raise BadRequest(f"Invalid Player Last Played Date: {e}")

    db.session.commit()

    return player.serialize()

@restapi.delete('/players/<int:id>')
@login_required
def deletePlayer(id):
    player_id = None

    try:
        player_id = sanitize_id(id)
    except (ValueError, TypeError) as e:
        raise BadRequest(f"Invalid Player ID: {e}")
    
    player = db.session.get(Player, player_id)
    if player is None:
        raise NotFound("Player not found.")
    
    if player.created_by != current_user:
        raise Unauthorized("You are not authorized to delete this resource.")
    
    db.session.delete(player)
    db.session.commit()

    return ('', 204)