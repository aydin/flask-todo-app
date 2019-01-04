from flask import Flask
from config import app_config
from db import db


def create_app_and_register_db(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    return app
