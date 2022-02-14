from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField


class TeamForm(FlaskForm):
    name = StringField('Enter Pokemon Name', validators=[DataRequired()])
    submit = SubmitField('Select')

class OpponentForm(FlaskForm):
    opponent = QuerySelectField('Select Your Opponent', get_label = 'full_name', validators=[DataRequired()])
    submit = SubmitField('Select')

class BattleForm(FlaskForm):
    icon = RadioField('SELECT YOUR METHOD OF ATTACK:', validators=[DataRequired()],
            choices=[(1, "Rock"),(2, "Paper"),(3,"Scissors")])
    submit = SubmitField('Select')