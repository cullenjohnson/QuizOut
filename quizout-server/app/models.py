from flask_login import UserMixin
import uuid
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped
from typing import List

from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.UUID, nullable=False, default = uuid.uuid4)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    created_players:Mapped[List["Player"]] = db.relationship(back_populates="created_by")

    def serialize(self):
        return {
            'id': self.id,
            'public_id': self.public_id,
            'email': self.email,
            'name': self.name
        }

class BuzzerClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.UUID, nullable=False, default = uuid.uuid4)
    ip = db.Column(db.String(25), nullable=False)
    teamBuzzerInfo = db.Column(db.JSON, nullable=False)

    def serialize(self):
        return {
            'ip': self.ip,
            'uuid': self.uuid,
            'teamBuzzerInfo': self.teamBuzzerInfo
        }
    
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    last_played:datetime = db.Column(db.DateTime, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by:Mapped["User"] = db.relationship(back_populates="created_players")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_played': self.last_played.isoformat()
        }