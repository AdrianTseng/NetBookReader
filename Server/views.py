__author__ = 'LimeQM'

from flask import render_template, redirect, flash, request, abort, jsonify
from jinja2 import TemplateNotFound
from . import app, login_manager, db
from .models import User, Chapters, Reading
from .blueprints.Users.SigninForm import SigninForm
from flask_login import login_user, login_required, current_user
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def extract_book_name(book_str):
    return book_str.split("_")[0]


@app.route('/')
@login_required
def home():
    user = current_user
    books = [each.get_progress() for each in user.books]
    books_name = [extract_book_name(each) for each in books]
    pending = [each for each in Chapters.get_books() if extract_book_name(each) not in books_name]
    return render_template("/partials/home.html", dev="vue/dist/vue.js" if app.debug else "vue",
                           user=user.username,
                           books=books,
                           pending=pending)


@app.route("/user", methods=["GET", "POST"])
def user():
    form = SigninForm()
    if form.validate_on_submit():
        _user = User.find(form.username.data)
        if _user and _user.verify_password(form.password.data):
            login_user(user=_user, remember=True, duration=timedelta(hours=3))
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            else:
                return redirect("/")
        flash("用户名或者密码错误")
    return render_template("/partials/user.html", dev="vue/dist/vue.js" if app.debug else "vue", form=form)


@app.route("/book/add", methods=["POST"])
@login_required
def add_book():
    data = str(request.form.get("book"))
    if Reading.exists(data, current_user.id):
        res = jsonify(success=False)
        res.status_code = 404
        return res

    reading = Reading(data, current_user.id)
    try:
        db.session.add(reading)
        db.session.commit()
        return jsonify(book=reading.get_progress())
    except SQLAlchemyError:
        db.session.rollback()
        res = jsonify(success=False)
        res.status_code = 404
        return res


@app.route("/book/remove", methods=["POST"])
@login_required
def remove_book():
    data = str(request.form.get("book"))
    reading = Reading.query.filter(Reading.book == data, Reading.user_id == current_user.id).first()
    try:
        db.session.delete(reading)
        db.session.commit()

        new_record = Chapters.get_last_chapter(data)
        return jsonify(book="%s_%s_%s" % (new_record.book, new_record.chapter, new_record.title))
    except SQLAlchemyError:
        db.session.rollback()
        res = jsonify(success=False)
        res.status_code = 404
        return res


@app.route("/menu/<path:book>", methods=["GET", "POST"])
@login_required
def get_menu(book):
    if request.method == "POST":
        reading = Reading.query.filter(Reading.book == book, Reading.user_id == current_user.id).first()
        reading.chapter_id = request.form.get("id")
        db.session.commit()
        return jsonify(book=reading.book)
    chapters = Chapters.query.filter_by(book=book).order_by(Chapters.index.desc()).all()
    return render_template("/partials/menu.html", dev="vue/dist/vue.js" if app.debug else "vue",
                           book=book, menus=[each.menu() for each in chapters])


@app.route("/read/<path:book>")
@login_required
def read_book(book):
    reading = Reading.query.filter(Reading.book == book, Reading.user_id == current_user.id).first()
    return render_template("/partials/read.html", dev="vue/dist/vue.js" if app.debug else "vue",
                           chapter_id=reading.chapter_id if reading is not None else None, book=book)


@app.route("/current/<path:this_chapter>")
@login_required
def this_chapter_content(this_chapter):
    chapter = Chapters.get(this_chapter)
    if chapter is not None:
        return jsonify(book=chapter.book, title="%s\t%s" % (chapter.chapter, chapter.title),
                   content=chapter.content, id=chapter.id)
    else:
        return abort(404)


@app.route("/next/<path:this_page>")
@login_required
def next_chapter_content(this_page):
    chapter = Chapters.get(this_page)
    reading = Reading.query.filter(Reading.book == chapter.book, Reading.user_id == current_user.id).first()
    reading.chapter_id = this_page
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
    next_chapter = Chapters.query.filter(Chapters.book == chapter.book, Chapters.index > chapter.index).\
        order_by(Chapters.index).first()
    if next_chapter is None:
        return jsonify(book=chapter.book, finished=True)
    return jsonify(book=next_chapter.book, title="%s\t%s" % (next_chapter.chapter, next_chapter.title),
                   content=next_chapter.content, id=next_chapter.id, finished=False)


@app.route('/partials/<path:content>.html')
def partials(content):
    try:
        return render_template("/partials/%s.html" % content, module=content)
    except TemplateNotFound:
        abort(404)
