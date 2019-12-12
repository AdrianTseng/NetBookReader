__author__ = 'LimeQM'

from flask import render_template, redirect, flash, request, abort, jsonify, send_from_directory, send_file
from jinja2 import TemplateNotFound
from . import app, login_manager, db
from .models import User, Chapters, Reading, Inventory
from .blueprints.Users.SigninForm import SigninForm
from flask_login import login_user, login_required, current_user, fresh_login_required
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from config import LOGIN_DAYS


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def extract_book_name(book_str):
    return book_str.split("_")[0]


@app.route('/')
@login_required
def home():
    user = current_user
    try:
        books = [each.get_progress() for each in user.books]
    except OperationalError:
        books = [each.get_progress() for each in user.books]
    books_name = [extract_book_name(each) for each in books]
    pending = [each for each in Chapters.get_books() if extract_book_name(each) not in books_name]
    return render_template("/partials/home.html", dev="vue/dist/vue.js" if app.debug else "vue",
                           user=user.username,
                           books=books,
                           pending=pending)


@app.route('/<path:filename>')
def send_static(filename):
    return send_from_directory("../static", filename)


@app.route("/user", methods=["GET", "POST"])
def user():
    form = SigninForm()
    if form.validate_on_submit():
        try:
            _user = User.find(form.username.data)
        except OperationalError:
            _user = User.find(form.username.data)
        if _user and _user.verify_password(form.password.data):
            login_user(user=_user, remember=True, duration=timedelta(days=LOGIN_DAYS))
            if (request.base_url in request.referrer) and ("user" not in request.referrer):
                return redirect(request.referrer)
            else:
                return redirect("/")
        flash("用户名或者密码错误")
    return render_template("/partials/user.html", dev="vue/dist/vue.js" if app.debug else "vue", form=form)


@app.route("/book/add", methods=["POST"])
@login_required
def add_book():
    data = str(request.form.get("book"))
    book = Inventory.get_book(data)
    if Reading.exists(book, current_user.id):
        res = jsonify(success=False)
        res.status_code = 404
        return res

    reading = Reading(book, current_user.id)
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
    book = Inventory.get_book(data)
    reading = Reading.query.filter(Reading.book == book, Reading.user_id == current_user.id).first()
    book.vacant_date = datetime.utcnow()
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
        book_item = Inventory.get_book(book)
        reading = Reading.query.filter(Reading.book == book_item, Reading.user_id == current_user.id).first()
        reading.chapter_id = request.form.get("id")
        db.session.commit()
        return jsonify(book=reading.book.book)
    chapters = Chapters.query.filter_by(book=book).order_by(Chapters.index.desc()).all()
    return render_template("/partials/menu.html", dev="vue/dist/vue.js" if app.debug else "vue",
                           book=book, menus=[each.menu() for each in chapters])


@app.route("/read/<path:book>")
@login_required
def read_book(book):
    book = Inventory.get_book(book)
    reading = Reading.query.filter(Reading.book == book, Reading.user_id == current_user.id).first()

    return render_template("/partials/read.html", dev="vue/dist/vue.js" if app.debug else "vue",
                           chapter_id=reading.chapter_id if reading is not None else None, book=book.book)


@app.route("/current/<path:this_chapter>")
@login_required
def this_chapter_content(this_chapter):
    try:
        chapter = Chapters.get(this_chapter)
    except OperationalError:
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
    book = Inventory.get_book(chapter.book)
    reading = Reading.query.filter(Reading.book == book, Reading.user_id == current_user.id).first()
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


@app.route("/download", methods=["POST"])
@login_required
def get_download_book():
    book = str(request.json["book"])
    return jsonify(data=Chapters.download(book))


@app.route("/book/search", methods=["POST"])
@login_required
def search_for_add_inventory():
    import requests
    from bs4 import BeautifulSoup

    book_name = request.form.get("book")

    prefix_url = "https://m.jx.la"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Referer': prefix_url
    }

    prefix_html = requests.get(prefix_url, headers)
    prefix_soup = BeautifulSoup(prefix_html.text, 'lxml')
    prefix_item = prefix_soup.select(".searchForm > input[type=hidden]")
    prefix_data = set(["%s=%s" % (each.get("name"), each.get("value")) for each in prefix_item])

    search_url = "https://sou.xanbhx.com/search?q=%s&%s" % (book_name, "&".join(prefix_data))
    search_html = requests.get(search_url, headers, verify=False)
    search_soup = BeautifulSoup(search_html.text, 'lxml')
    search_item = search_soup.select("body > div.recommend.mybook > div.hot_sale > a")
    search_result = [{"book": item.select_one(".title").text.strip(),
                      "author": item.select_one(".author").text.strip().split("：")[1],
                      "url": item.attrs["href"]} for item in search_item]

    return jsonify(data=search_result)


@app.route("/book/collect", methods=["POST"])
@login_required
def collect_for_inventory():
    book_name = request.form.get("book")
    author = request.form.get("author")
    book_url = request.form.get("url")

    user = current_user

    if Inventory.exists(book_url):
        return jsonify(data={"reason": "这本书我们已经收藏了，去库存中看看吧！"})

    added_books = user.added_books
    if not user.admin and len(added_books) > 0:
        latest_collect_date = max([each.added_date for each in added_books])
        if latest_collect_date + timedelta(days=1) > datetime.utcnow():
            return jsonify(data={"reason": "为了保证服务器资源，普通用户一天只能添加一本书。。"})

    new_book = Inventory(book_name, author, book_url)
    new_book.user = user

    db.session.add(new_book)
    db.session.commit()

    return jsonify(data={"reason": "收藏成功，我们要先准备一下，等过一段时间再去库存中看看吧。"})


