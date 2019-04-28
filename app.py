#!env/bin/python3

__author__ = 'LimeQM'

from Server import app, db
from flask_migrate import Migrate

migrate = Migrate(app, db)


class debug():
    app = app

    def run(self):
        app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    # db.create_all(app=app)
    # db.session.commit()
    app.run(host='0.0.0.0', debug=True)
