from flask import session, redirect, url_for, render_template, request, current_app, flash, jsonify, g
from . import main
from .user import User, Room, Message
from app import db
from .forms import JoinForm, SignupForm, LoginForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_login import current_user



@main.route('/')
def home():
    return render_template('home.html')


@main.route('/options')
def options():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        profile_picture = None
        if user.profile_picture:
            profile_picture = url_for('static', filename='profile_pics/' + user.profile_picture)
        return render_template('options.html', user=user, profile_picture=profile_picture)
    else:
        return redirect(url_for('main.home'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        #checking id user already exist in database
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user or existing_email:
            message = "username or email already exists. please log in."
            return render_template('signup.html', form=form, message=message)
        
        #if user not in database, create new
        user = User(username=username, email=email, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception as error:
            db.session.rollback()
            message = f"Error: {error}"
            return render_template('signup.html', form=form, message=message)

    return render_template('signup.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        # MINE Store username details in session
        session['username'] = username
    
        if user:
            if user.password == password:
                session['username'] = user.username
                return redirect(url_for('.options'))
            else:
                message = "Invalid username or password. Please try again."
        else:
            message = "User does not exist. Please sign up."

        return render_template('login.html', form=form, message=message)

    return render_template('login.html', form=form)


@main.route('/create', methods=['GET', 'POST'])
def create():
    form = JoinForm()
    if form.validate_on_submit():
        room_name = form.room_name.data
        room_id = form.room_id.data

        #check if room name and id exist in database
        existing_room = Room.query.filter_by(room_name=room_name, room_id=room_id).first()
        if existing_room:
            message = 'Room already exist, please join.'
            return render_template('create.html', form=form, message=message)

        #create new room
        room = Room(room_name=room_name, room_id=room_id)
        try:
            db.session.add(room)
            db.session.commit()

            # Store room details in session
            session['room_name'] = room.room_name
            session['room_id'] = room.room_id
            return redirect(url_for('main.chat'))
        
        except Exception as error:
            db.session.rollback()
            message = f"Error: {error}"
            return render_template('create.html', form=form, message=message)

    return render_template('create.html', form=form)


@main.route('/join', methods=['GET', 'POST'])
def join():
    """Login form to enter a room."""
    form = JoinForm()
    if form.validate_on_submit():
        room_name = form.room_name.data
        room_id = form.room_id.data

        room = Room.query.filter_by(room_name=room_name, room_id=room_id).first()
        if room:
            session['room_name'] = room.room_name
            session['room_id'] = room.room_id

            return redirect(url_for('.chat'))
        else:
            message = "Invalid room details. Please try again."
            return render_template('join.html', form=form, message=message)

    elif request.method == 'GET':
        form.room_name.data = session.get('room_name', '')
        form.room_id.data = session.get('room_id', '')

    return render_template('join.html', form=form)


@main.route('/chat', methods=['GET', 'POST'])
def chat():
    # Get the room name and username from the session
    room_name = session.get('room_name')
    username = session.get('username')

    # Get the current user based on the username
    user = User.query.filter_by(username=username).first()

    if not user:
        # If the user doesn't exist, create a new user
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    # Get or create the room based on the room name
    room = Room.query.filter_by(room_name=room_name).first()

    if not room:
        # If the room doesn't exist, create a new room
        room = Room(room_name=room_name)
        db.session.add(room)
        db.session.commit()

    # Store current_room in g object for access in the template
    g.current_room = room    
    g.current_user = current_user
    
    # Get the profile picture for the current user
    profile_picture = user.profile_picture 

    # Get the messages for the current room and user
    messages = Message.query.filter_by(room_id=room.id).all()

    return render_template('chat.html', room_name=room_name, username=username, profile_picture=profile_picture, messages=messages, current_user=g.current_user)


@main.route('/save_message', methods=['POST'])
def save_message():
    if request.method == 'POST':
        data = request.get_json()
        msg = data.get('msg')
        room_id = data.get('room_id')
        username = session.get('username')  # Get the sender's username from the session
        # Get the current user based on the username
        user = User.query.filter_by(username=username).first()

        if msg and room_id and user:
            # Create a new Message object
            new_message = Message(content=msg, timestamp=datetime.utcnow(), room_id=room_id, user_id=user.id)

            # Add the message to the database
            db.session.add(new_message)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Message saved successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Error saving the message. Missing data.'})

@main.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('main.home'))

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('main.home'))

    profile_picture = user.profile_picture if user.profile_picture else 'prof.jpg'
    profile_picture_path = url_for('static', filename=f'profile_pics/{profile_picture}')

    return render_template('profile.html', user=user, profile_picture=profile_picture_path)


@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # Update profile picture
        file = request.files['profile_picture']
        if file:
            filename = secure_filename(file.filename)
            profile_pics_folder = current_app.config['PROFILE_PICS_FOLDER']
            file.save(os.path.join(profile_pics_folder, filename))
            user.profile_picture = filename

        # Update user information
        user.name = request.form['name']
        user.username = request.form['username']
        user.email = request.form['email']
        user.age = int(request.form['age']) if request.form['age'] else None
        user.gender = request.form['gender']
        user.birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d') if request.form['birthdate'] else None

        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('main.options'))
        except Exception as error:
            db.session.rollback()
            flash(f'Error: {error}', 'danger')
            return redirect(url_for('main.edit_profile'))
    return render_template('edit_profile.html', user=user)


@main.route('/view-room')
def view_room():
    rooms = Room.query.all()
    users = User.query.all()
    messages = Message.query.all()
    return render_template('rooms.html', rooms=rooms, users=users, messages=messages)

