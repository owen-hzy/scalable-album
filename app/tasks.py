import os
import PIL.Image
from celery import Celery


def make_celery():
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    celery.app = app
    return celery

celery = make_celery()

@celery.task
def process_image(image_name):
    image = PIL.Image.open(os.path.join(celery.app.config["UPLOAD_FOLDER"], image_name))
    image.thumbnail(celery.app.config["THUMBNAIL_SIZE"])
    image.save(os.path.join(celery.app.config["THUMBNAIL_FOLDER"], image_name))

