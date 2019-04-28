from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config


app = Flask(__name__, static_folder='../static')
app.config.from_object(config)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "user"
login_manager.init_app(app=app)

# app.jinja_env.variable_start_string = '{{ '
# app.jinja_env.variable_end_string = ' }}'

from . import views, models

from .blueprints.Home import home
from .blueprints.Users import user

app.register_blueprint(home)
app.register_blueprint(user)
