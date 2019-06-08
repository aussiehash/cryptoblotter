from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from cryptoalpha.models import User
from wtforms import StringField, PasswordField, \
    SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo,\
    ValidationError


class ImportCSV(FlaskForm):
    csvfile = FileField('Import CSV File', validators=[FileAllowed(['csv'])])
    submit = SubmitField('Open')

    def validate_csvfile(sef, csvfile):
        if csvfile.data is None:
            raise ValidationError("Please select a file")


class ContactForm(FlaskForm):
    email = StringField('Your email (optional)')
    message = TextAreaField('Your message')
    submit = SubmitField('Send message')
