import redis
from celery import Celery
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
import os

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
cache = redis.StrictRedis(host="localhost")

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"

def create_app(config_name, app_name):
    app = Flask(__name__)
    app.name = app_name
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.mkdir(app.config["UPLOAD_FOLDER"])
    if not os.path.exists(app.config["THUMBNAIL_FOLDER"]):
        os.mkdir(app.config["THUMBNAIL_FOLDER"])

    return app

def create_celery_app(app=None):
    app = app or create_app("default", "app")
    celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery