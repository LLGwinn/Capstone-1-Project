""" SQLAlchemy models for reloc_asst """

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """ Connect db to Flask app """

    db.app = app
    db.init_app(app)

############### MODELS ###################

class Geocode(db.Model):
    """ Census Bureau state and place codes for all cities """

    __tablename__ = 'geocodes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    state = db.Column(
        db.Text
    )

    place = db.Column(
        db.Text
    )

    name = db.Column(
        db.Text
    )

    abbr = db.Column(
        db.Text
    )

    def __repr__(self):
        return f'<Geocode: state={self.state}, place={self.place}, name={self.name}>'

class User(db.Model):
    """ Users with accounts """

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
            db.Text,
            nullable=False,
        )

    email = db.Column(
        db.Text,
        nullable=False
    )

    current_city = db.Column(
        db.Integer,
        db.ForeignKey('geocodes.id'),
        nullable=False
    )

    favorites = db.relationship('Geocode', secondary='favorites', backref='users')
    cities = db.relationship('Geocode', backref='user_ids')

    def __repr__(self):
        return f'<User #{self.id}: {self.username}>'


    @classmethod
    def register(cls, username, password, email, curr_city):
        """ Create account for user, add to db """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            current_city=curr_city
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """ Search for a username/password match.
            If found, return user object.
            Else, return False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class User_Favorites(db.Model):
    """ Join table - map user to cities they have favorited """

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable=False
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey('geocodes.id', ondelete='cascade'),
        unique=True,
        nullable=False
    )

        
