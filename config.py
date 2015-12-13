import os

class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "ierg4080-project"
    # required by Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ierg4080:ierg4080@localhost/project"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    IMAGES_PER_PAGE=9
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app/static/images")
    THUMBNAIL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app/static/thumbnails")
    CELERY_BROKER_URL = "amqp://localhost"
    THUMBNAIL_SIZE = (300, 300)

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig
}