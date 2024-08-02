from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Email

class SignupForm(FlaskForm):
    """Accepts user registration information."""
    username = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    """Accepts login information."""
    username = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class JoinForm(FlaskForm):
    """Accepts room information for joining a room."""
    room_name = StringField('Room name', validators=[DataRequired()])
    room_id = StringField('Room Id', validators=[DataRequired()])
    submit = SubmitField('Join Room')