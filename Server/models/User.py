from flask_login import UserMixin
from Server import db
from sqlalchemy.dialects.postgresql import UUID
from flask_bcrypt import generate_password_hash, check_password_hash
import uuid
from config import SECURITY
from sqlalchemy.exc import OperationalError


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.BOOLEAN(), default=False, nullable=False)
    books = db.relationship('Reading', backref='books', lazy=True)
    added_books = db.relationship("Inventory", back_populates="user")

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
        try:
            res = User.query.get(user_id)
        except OperationalError:
            res = User.query.get(user_id)

        return res
