import hashlib
import os
import random

from app import db
from app.main.forms import EditProfileForm, UploadForm, SearchForm
from app.models import User, Image
from flask import render_template, url_for, flash, redirect, request, current_app, make_response
from flask.ext.login import login_required, current_user
from . import main

@main.route("/test")
def test():
    return current_app.name

@main.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()
    if request.method == "POST" and form.validate_on_submit():
        return redirect(url_for(".search", query=form.search.data))
    page = request.args.get("page", 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ""))
    if show_followed:
        query = current_user.followed_images
    else:
        query = Image.query
    pagination = query.order_by(Image.timestamp.desc()).paginate(page, per_page=current_app.config["IMAGES_PER_PAGE"], error_out=False)
    images = pagination.items
    return render_template("index.html", images=images, pagination=pagination, form=form, show_followed=show_followed)

@main.route("/search")
@login_required
def search():
    query = request.args.get("query")
    page = request.args.get("page", 1, type=int)
    pagination = Image.query.filter(Image.hashtags.like("%" + query + "%")).order_by(Image.timestamp.desc()).paginate(page, per_page=current_app.config["IMAGES_PER_PAGE"], error_out=False)
    images = pagination.items
    return render_template("search_results.html", images=images, pagination=pagination, query=query)

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
            os.remove(os.path.join(current_app.config["THUMBNAIL_FOLDER"], image.image_name))
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
        hashtags = form.hashtags.data
        filename, extension = (form.image.data.filename.rsplit(".", 1)[0], form.image.data.filename.rsplit(".", 1)[1])
        # randomize the file name to avoid override the image with same name
        filename = filename + str(random.random())
        filename = hashlib.md5(filename.encode("utf-8")).hexdigest() + "." + extension
        form.image.data.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        from ..tasks import process_image
        process_image.delay(filename, hashtags, current_user._get_current_object())

        flash("Successfully uploaded")
        # return redirect(url_for("."))
        return redirect(url_for(".details", image_name=filename))
    return render_template("new_image.html", form=form)

@main.route("/details/<image_name>", methods=["GET"])
@login_required
def details(image_name):
    return render_template("details.html", image=image_name)

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

@main.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid User")
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash("You are already following this user")
        return redirect(url_for(".user", username=username))
    current_user.follow(user)
    flash("You are now following %s" % username)
    return redirect(url_for(".user", username=username))

@main.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid User")
        return redirect(url_for(".index"))
    if not current_user.is_following(user):
        flash("You are not following this user")
        return redirect(url_for(".user", username=username))
    current_user.unfollow(user)
    flash("You are not following %s anymore" % username)
    return redirect(url_for(".user", username=username))

@main.route("/followers/<username>")
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("Invalid User")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config["FOLLOWERS_PER_PAGE"], error_out=False)
    follows = [{"user": item.follower, "timestamp": item.timestamp} for item in pagination.items]
    return render_template("followers.html", user=user, title="Followers of",
                           endpoint=".followers", pagination=pagination, follows=follows)

@main.route("/followed-by/<username>")
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config["FOLLOWERS_PER_PAGE"], error_out=False)
    follows = [{"user": item.followed, "timestamp": item.timestamp} for item in pagination.items]
    return render_template("followers.html", user=user, title="Followed by",
                           endpoint=".followed_by", pagination=pagination, follows=follows)

@main.route("/all")
@login_required
def show_all():
    res = make_response(redirect(url_for(".index")))
    res.set_cookie("show_followed", "", max_age=10*24*60*60)
    return res

@main.route("/followed")
@login_required
def show_followed():
    res = make_response(redirect(url_for(".index")))
    res.set_cookie("show_followed", "1", max_age=10*24*60*60)
    return res