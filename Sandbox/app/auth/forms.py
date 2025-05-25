from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import (
    DataRequired, Email, EqualTo, ValidationError, Length, 
    Regexp
)
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters'),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 
               message='Usernames must start with a letter and can only contain letters, numbers, dots or underscores')
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=64, message='First name must be less than 64 characters'),
        Regexp('^[A-Za-z\s-]*$', message='First name can only contain letters, spaces, and hyphens')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=64, message='Last name must be less than 64 characters'),
        Regexp('^[A-Za-z\s-]*$', message='Last name can only contain letters, spaces, and hyphens')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp('^(?=.*[A-Za-z])(?=.*\d)', message='Password must contain at least one letter and one number')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    is_admin = BooleanField('Administrator Access')
    submit = SubmitField('Register User')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp('^(?=.*[A-Za-z])(?=.*\d)', message='Password must contain at least one letter and one number')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
