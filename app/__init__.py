from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
import redis
import json
import os

socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()

def create_app(debug=True, host='0.0.0.0:5000'):
    app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')
    app.config['DEBUG'] = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    # SQLite database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #path to store profile pics
    #app.config['PROFILE_PICS_FOLDER'] = os.path.join(app.root_path, 'profile_pics')
    profile_pics_folder = os.path.join(app.static_folder, 'profile_pics')
    os.makedirs(profile_pics_folder, exist_ok=True)
    app.config['PROFILE_PICS_FOLDER'] = profile_pics_folder

    messages_folder = os.path.join(app.static_folder, 'massages' )
    os.makedirs(messages_folder, exist_ok=True)
    app.config['MASSAGES_FOLDER'] = messages_folder
    
    #set flask-socketio options
    app.config['FLASK_DEBUG'] = debug
    app.config['FLASK_USE_RELOADER'] = False
    app.config['FLASK_USE_DEBUGGER'] = False

    socketio.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


