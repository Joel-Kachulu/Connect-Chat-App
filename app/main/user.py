from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(130), unique=True, nullable=True)
    password = db.Column(db.String(100))
    profile_picture = db.Column(db.String(100), default='default.jpg')
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    birthdate = db.Column(db.Date)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room', backref='users')

    def __repr__(self):
        return f'<User {self.username}>'
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_message_user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', name='fk_message_room_id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref='messages')
    room = db.relationship('Room', backref='messages')

    def __repr__(self):
        return f'<Message {self.content}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(150), unique=True, nullable=True)
    room_id = db.Column(db.String(50), unique=True)
    
    def __repr__(self):
        return f'<Message {self.room_name}>'
    