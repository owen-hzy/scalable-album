from app import db
from ..models import Image

def insert_image(image_name, hashtags, user):
    image = Image(image_name=image_name, user=user, hashtags=hashtags)
    try:
        db.session.add(image)
        db.session.commit()
    except:
        db.session.rollback()