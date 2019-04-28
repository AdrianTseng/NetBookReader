from flask_login import UserMixin
from Server import db
from sqlalchemy.dialects.postgresql import UUID
from flask_bcrypt import generate_password_hash, check_password_hash
import uuid
from config import SECURITY


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    books = db.relationship('Reading', backref='books', lazy=True)

    def __init__(self, username):
        self.username = username
        self.id = self.get_id()

    def __repr__(self):
        return "<User: %r>" % self.username

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, SECURITY["iterations"]).decode("utf-8")

    def verify_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        if self.id is not None:
            return self.id
        else:
            return uuid.uuid4()

    @staticmethod
    def find(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get(user_id):
        return User.query.get(user_id)
