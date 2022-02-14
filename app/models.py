from app import db, login
from flask_login import UserMixin # this is just for the user model!
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import column_property

class UserPokemon(db.Model):
    poke_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    full_name = column_property(first_name + " " + last_name)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    pokemen = db.relationship('Pokemon', secondary='user_pokemon', backref='users', lazy='dynamic')
    results = db.relationship('Result', backref='users2')

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = self.hash_password(data['password'])

    # saves user to database
    def save(self):
        db.session.add(self)
        db.session.commit()

class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    ability = db.Column(db.String(150))
    sprite = db.Column(db.Text)

    def __repr__(self):
        return f'<Post: {self.id} | {self.name}>'
    
    def save(self):
        db.session.add(self) # add the user to the db session
        db.session.commit() #save everything in the session to the database

    def from_dict(self, data):
        self.name = data['name']
        self.hp = data['hp']
        self.attack = data['attack']
        self.defense = data['defense']
        self.ability = data['ability']
        self.sprite = data['sprite']

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(150))
    selection = db.Column(db.String(150))
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Result: {self.id} | {self.result}>'

    def from_dict(self, data):
        self.result = data['result']
        self.selection = data['selection']
        self.user_id = data['user_id']

    def save(self):
        db.session.add(self)
        db.session.commit()        

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
        