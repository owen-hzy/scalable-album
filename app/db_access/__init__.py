from app import db
from ..models import Image
from flask.ext.login import current_user

def insert_image(image_name):
    image = Image(image_name=image_name, user=current_user._get_current_object())
    try:
        db.session.add(image)
        db.session.commit()
    except:
        db.session.rollback()