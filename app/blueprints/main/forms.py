from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from app.models import User

class EntryForm(FlaskForm):
    name = StringField('Enter Pokemon Name', validators=[DataRequired()])
    submit = SubmitField('Submit')