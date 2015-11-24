from app import db
from app.main.forms import EditProfileForm, NoteForm
from app.models import User, Note
from flask import render_template, url_for, flash, redirect, request, current_app
from flask.ext.login import login_required, current_user
from . import main

@main.route("/", methods=["GET", "POST"])
def index():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(body=form.body.data, user=current_user._get_current_object())
        try:
            db.session.add(note)
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = Note.query.order_by(Note.timestamp.desc()).paginate(page, per_page=current_app.config["NOTES_PER_PAGE"], error_out=False)
    notes = pagination.items
    return render_template("index.html", form=form, notes=notes, pagination=pagination)

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.notes.order_by(Note.timestamp.desc()).paginate(page, per_page=current_app.config["NOTES_PER_PAGE"], error_out=False)
    notes = pagination.items
    return render_template("user.html", user=user, notes=notes, pagination=pagination)

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