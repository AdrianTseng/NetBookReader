from Server import db
from sqlalchemy.dialects.postgresql import UUID
from .User import User
import uuid


class BookLists(db.model):
    __tablename__ = "book_lists"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    book = db.Column(db.String(32), nullable=False)
    url = db.Column(db.String(128), unique=True, nullable=False)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship('User', backref=db.backref('added_books'))

    def __init__(self, book, author, url):
        self.id = uuid.uuid4()
        self.book = book
        self.url = url

    def __repr__(self):
        if self.user is not None:
            return "<<%r>>(Added by: %s): %r" % (self.book, self.user.username, self.url)
        else:
            return "<<%r>>: %r" % (self.book, self.url)

    @staticmethod
    def get_books(book):
        return BookLists.query.filter_by(book=book).all()
