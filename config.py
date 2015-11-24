class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "ierg4080-project"
    # required by Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ierg4080:ierg4080@localhost/project"
    NOTES_PER_PAGE=10

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig
}