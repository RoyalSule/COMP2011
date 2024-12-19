from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from .models import User

class LoginForm(FlaskForm):
    username = StringField('Username*', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password*', validators=[DataRequired()])
    submit = SubmitField('LOG IN')

class RegisterForm(FlaskForm):
    username = StringField('Username*', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password*', validators=[DataRequired()])
    submit = SubmitField('CREATE ACCOUNT')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists. Please choose a different one.')

