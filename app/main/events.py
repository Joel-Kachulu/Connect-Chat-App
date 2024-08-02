from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from .user import Message, Room
from app import db
from .user import User
from datetime import datetime

@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room_name = session.get('room_name')
    username = session.get('username')

    if room_name and username:
        join_room(room_name)
        emit('status', {'msg': username + ' has entered the room.'}, room=room_name, broadcast=True)
    else:
        # Handle the case when either 'room_name' or 'username' is missing
        emit('status', {'msg': 'A user has entered the room.'}, room_name=room_name, broadcast=True)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user enters a new message.
    The message is saved to the database and sent to all people in the room."""
    room_name = session.get('room_name')
    username = session.get('username')

    if room_name and username:
        # Get the current user based on the username
        user = User.query.filter_by(username=username).first()

        # Get the room based on the room name
        room = Room.query.filter_by(room_name=room_name).first()

        if user and room:
            # Create a new Message object
            new_message = Message(content=message['msg'], timestamp=datetime.utcnow(), user_id=user.id, room_id=room.id)

            # Add the message to the database
            db.session.add(new_message)
            db.session.commit()

            # Emit the message to all clients in the room (including the sender)
            emit('message', {'msg': username + ': ' + message['msg'], 'sender': 'me'}, room=room_name, include_self=True)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room_name = session.get('room_name')
    username = session.get('username')

    if room_name:
        leave_room(room_name)
        emit('status', {'msg': username + ' has left the room.'}, room=room_name, broadcast=True)




