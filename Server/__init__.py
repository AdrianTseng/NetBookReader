from flask import Flask
from flask_wtf import CSRFProtect
# from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config

'''
class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True
'''


REMEMBER_COOKIE_DURATION = 24 * 60 * 60 * config.LOGIN_DAYS

app = Flask(__name__, static_folder='../static')
app.config.from_object(config)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.session_protection = "basic"
login_manager.login_view = "user"
login_manager.login_message = "请先登陆以访问本页面"
login_manager.init_app(app=app)

# app.jinja_env.variable_start_string = '{{ '
# app.jinja_env.variable_end_string = ' }}'

from . import views, models

from .models import BannedUrls

from .blueprints.Home import home
from .blueprints.Users import user

app.register_blueprint(home)
app.register_blueprint(user)
