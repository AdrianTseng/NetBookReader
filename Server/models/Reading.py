from Server import db
from .Chapters import Chapters
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Reading(db.Model):
    __tablename__ = "reading"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    book = db.Column(db.String(32), nullable=False)
    progress = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    chapter_id = db.Column(UUID(as_uuid=True), db.ForeignKey("chapters.id"), nullable=False)

    def __init__(self, book, user_id):
        self.book = book
        self.id = uuid.uuid4()
        self.user_id = user_id
        chapter = Chapters.get_first_chapter(book)
        self.chapter_id, self.progress = chapter.id, chapter.index

    def __repr__(self):
        return "<User: %r>: 《%r》" % (self.user_id, self.book)

    def get_progress(self):
        chapter = Chapters.get(self.chapter_id)
        return "%s_%s_%s_%s" % (self.book, chapter.chapter, chapter.title, chapter.id)

    @staticmethod
    def exists(book, user_id):
        return Reading.query.filter(Reading.book == book, Reading.user_id == user_id).count() > 0


