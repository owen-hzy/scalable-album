from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import Length, DataRequired, Regexp

class EditProfileForm(Form):
    name = StringField("Real Name", validators=[Length(1, 64)])
    location = StringField("Location", validators=[Length(1, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField("Submit")

class UploadForm(Form):
    image = FileField("Upload Image Here", validators=[DataRequired()])
    submit = SubmitField("Submit")