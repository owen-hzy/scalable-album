import PIL.Image
import os
from app import create_celery_app
from app.db_access import insert_image

celery = create_celery_app()

@celery.task(name="app.process_image")
def process_image(image_name, hashtags, user):
    insert_image(image_name, hashtags, user)
    image = PIL.Image.open(os.path.join(celery.conf["UPLOAD_FOLDER"], image_name))
    image.thumbnail(celery.conf["THUMBNAIL_SIZE"])
    image.save(os.path.join(celery.conf["THUMBNAIL_FOLDER"], image_name))

