__author__ = 'LimeQM'

from flask import Blueprint

user = Blueprint('users', __name__, template_folder='./templates', url_prefix='/user')
