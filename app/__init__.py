from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.cache import Cache
from flask.ext.pymongo import PyMongo

from app.config import config


bootstrap = Bootstrap()
cache = Cache()
mongo = PyMongo()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    cache.init_app(app)
    mongo.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
