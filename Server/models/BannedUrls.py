# -*- coding: utf-8 -*-
# @Time    : 2019/10/23 上午10:30
# @Author  : 郑启明
# @File    : BannedUrls.py

from Server import db


class BannedUrls(db.Model):
    __tablename__ = "banned_url"

    url = db.Column(db.String(128), unique=True, nullable=False, primary_key=True)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "Banned URL: <<%r>>" % self.url

    @staticmethod
    def all():
        return BannedUrls.query.all()