from Server import db
from sqlalchemy.dialects.postgresql import UUID
from .User import User
import uuid
from datetime import datetime


class Inventory(db.Model):
    __tablename__ = "inventories"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    book = db.Column(db.String(32), nullable=False)
    author = db.Column(db.String(32), nullable=True)
    url = db.Column(db.String(128), unique=True, nullable=False)
    added_date = db.Column(db.DateTime(), default=datetime.utcnow)

    readings = db.relationship("Reading", back_populates="book")
    vacant_date = db.Column(db.DateTime(), default=datetime.utcnow)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates="added_books")

    def __init__(self, book, author, url):
        self.id = uuid.uuid4()
        self.author = author
        self.book = book
        self.url = url

    def __repr__(self):
        if self.user is not None:
            return "<<%r>>(Added by: %s): %r" % (self.book, self.user.username, self.url)
        else:
            return "<<%r>>: %r" % (self.book, self.url)

    @staticmethod
    def exists(url):
        return Inventory.query.filter_by(url=url).count() > 0

    @staticmethod
    def get_book(book_name):
        return Inventory.query.filter_by(book=book_name).first()