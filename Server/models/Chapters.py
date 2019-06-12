from Server import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Chapters(db.Model):
    __tablename__ = "chapters"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    url = db.Column(db.String(128), unique=True, nullable=False)
    book = db.Column(db.String(32), nullable=False)
    chapter = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    index = db.Column(db.Integer(), nullable=False)
    content = db.Column(db.Text(), nullable=False)

    readers = db.relationship("Reading", backref="chapter", lazy=True)

    def __init__(self, url, book, chapter, title, index, content):
        self.id = uuid.uuid4()
        self.url = url
        self.book = book
        self.chapter = chapter
        self.title = title
        self.index = index
        self.content = content

    def __repr__(self):
        return "<<%r>>: %r" % (self.book, self.chapter)

    @staticmethod
    def get_books():
        books = [each.book for each in Chapters.query.distinct(Chapters.book)]
        last_chapters = [Chapters.query.filter_by(book=book).order_by(Chapters.index.desc()).first() for book in books]
        return ["%s_%s_%s" % (chapter.book, chapter.chapter, chapter.title)
                for chapter in last_chapters]

    @staticmethod
    def get_first_chapter(book_name):
        chapter = Chapters.query.filter_by(book=book_name).order_by(Chapters.index).first()
        return chapter

    @staticmethod
    def get_last_chapter(book_name):
        chapter = Chapters.query.filter_by(book=book_name).order_by(Chapters.index.desc()).first()
        return chapter

    @staticmethod
    def get(chapter_id):
        return Chapters.query.get(chapter_id)

    @staticmethod
    def download(book_name):
        chapters = Chapters.query.filter_by(book=book_name).order_by(Chapters.index).all()

        doc = ""
        doc += "#%s\n\n" % book_name

        for c in chapters:
            doc += "\n\n##%s %s\n\n" % (c.chapter, c.title)
            doc += c.content

        return doc

    def menu(self):
        return "%s\t%s_%s" % (self.chapter, self.title, self.id)
