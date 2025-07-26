from flask_login import UserMixin
import uuid
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.UUID, nullable=False, default = uuid.uuid4)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

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