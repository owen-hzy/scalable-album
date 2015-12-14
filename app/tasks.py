import PIL.Image
import os, pickle
from app import create_celery_app, cache
from app.db_access import insert_image
from skimage.measure import structural_similarity as ssim
from skimage import io, color
from celery.contrib import rdb
import numpy as np

celery = create_celery_app()

@celery.task(name="app.process_image")
def process_image(image_name, hashtags, user):
    image_files = os.listdir(celery.conf["THUMBNAIL_FOLDER"])
    insert_image(image_name, hashtags, user)
    image = PIL.Image.open(os.path.join(celery.conf["UPLOAD_FOLDER"], image_name))
    image.thumbnail(celery.conf["THUMBNAIL_SIZE"])
    image = image.resize(celery.conf["THUMBNAIL_SIZE"], PIL.Image.ANTIALIAS)
    image.save(os.path.join(celery.conf["THUMBNAIL_FOLDER"], image_name))

    similarity = cal_similarity(image_name, image_files, celery.conf["THUMBNAIL_FOLDER"])
    cache.set(image_name, pickle.dumps(similarity, pickle.HIGHEST_PROTOCOL))

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

def cal_similarity(image_name, image_files, directory):
    # rdb.set_trace()
    original = io.imread(os.path.join(directory, image_name))
    original = rgb2gray(original)
    similarity = {}
    for image in image_files:
        if image_name != image:
            compare = rgb2gray(io.imread(os.path.join(directory, image)))
            sim = ssim(original, compare)
            if len(similarity) >= 2:
                min_ssim = min(similarity, key=similarity.get)
                if sim > similarity[min_ssim]:
                    del similarity[min_ssim]
                else:
                    continue
            similarity[image] = sim

            # update the cache
            if image in cache.keys():
                image_similarity = pickle.loads(cache.get(image))
                if len(image_similarity) < 2:
                    image_similarity[image_name] = sim
                    cache.set(image, pickle.dumps(image_similarity, pickle.HIGHEST_PROTOCOL))
                min_ssim = min(image_similarity, key=image_similarity.get)
                if sim > image_similarity[min_ssim]:
                    del image_similarity[min_ssim]
                    image_similarity[image_name] = sim
                    cache.set(image, pickle.dumps(image_similarity, pickle.HIGHEST_PROTOCOL))
    return similarity
