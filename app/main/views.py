import hashlib
import os
import random

from app import db
from app.main.forms import EditProfileForm, UploadForm
from app.models import User, Image
from flask import render_template, url_for, flash, redirect, request, current_app
from flask.ext.login import login_required, current_user
from . import main

@main.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    pagination = Image.query.order_by(Image.timestamp.desc()).paginate(page, per_page=current_app.config["IMAGES_PER_PAGE"], error_out=False)
    images = pagination.items
    return render_template("index.html", images=images, pagination=pagination)

@main.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.images.order_by(Image.timestamp.desc()).paginate(page, per_page=current_app.config["IMAGES_PER_PAGE"], error_out=False)
    images = pagination.items
    return render_template("user.html", user=user, images=images, pagination=pagination)

@main.route("/delete/<id>")
@login_required
def delete(id):
    image = Image.query.filter_by(id=id).first_or_404()
    if current_user == image.user:
        try:
            db.session.delete(image)
            db.session.commit()
            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], image.image_name))
        except:
            db.session.rollback()
        flash("Successfully deleted the image")
    else:
        flash("You can only delete your image")
    return redirect(request.referrer)

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()
    if request.method == "POST" and form.validate_on_submit():
        if not form.image.data and not form.image.data.mimetype.startswith("image"):
            return "Invalid File"
        filename, extension = (form.image.data.filename.rsplit(".", 1)[0], form.image.data.filename.rsplit(".", 1)[1])
        # randomize the file name to avoid override the image with same name
        filename = filename + str(random.random())
        filename = hashlib.md5(filename.encode("utf-8")).hexdigest() + "." + extension
        form.image.data.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        image = Image(image_name=filename, user=current_user._get_current_object())
        try:
            db.session.add(image)
            db.session.commit()
        except:
            db.session.rollback()
        flash("Successfully uploaded")
        return redirect(url_for(".index"))
    return render_template("new_image.html", form=form)

@main.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        try:
            db.session.add(current_user)
            db.session.commit()
        except:
            db.session.rollback()
        flash("Your profile has been updated")
        return redirect(url_for(".user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)