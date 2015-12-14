from datetime import datetime

from flask import request
from . import db, login_manager
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.TEXT())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    images = db.relationship("Image", backref="user", lazy="dynamic")

    followed = db.relationship("Follow",
                            foreign_keys=[Follow.follower_id],
                            backref=db.backref("follower", lazy="joined"),
                            lazy="dynamic",
                            cascade="all, delete-orphan")
    followers = db.relationship("Follow",
                            foreign_keys=[Follow.followed_id],
                            backref=db.backref("followed", lazy="joined"),
                            lazy="dynamic",
                            cascade="all, delete-orphan")


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in xrange(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        try:
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()

    def gravatar(self, size=100, default="identicon", rating="g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
        hash = self.avatar_hash or hashlib.md5(self.email.encode("utf-8")).hexdigest()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            try:
                db.session.add(f)
                db.session.commit()
            except:
                db.session.rollback()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            try:
                db.session.delete(f)
                db.session.commit()
            except:
                db.session.rollback()

    def __repr__(self):
        return "<User %r>" % (self.username)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    hashtags = db.Column(db.String(64), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in xrange(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Image(image_name="test.jpg",
                     timestamp=forgery_py.date.date(True),
                     hashtags=forgery_py.lorem_ipsum.word(),
                     user=u)
            db.session.add(p)
            try:
                db.session.commit()
            except:
                db.session.rollback()

    def __repr__(self):
        return "<Image %r>" % (self.hashtags)