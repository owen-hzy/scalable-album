from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import Length, DataRequired


class EditProfileForm(Form):
    name = StringField("Real Name", validators=[Length(1, 64)])
    location = StringField("Location", validators=[Length(1, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")

class NoteForm(Form):
    body = TextAreaField("Write your note here:", validators=[DataRequired()])
    submit = SubmitField("Submit")