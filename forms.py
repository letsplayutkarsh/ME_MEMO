from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired(), Length(min=2,max=20)])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField('Login')

class WriteForm(FlaskForm):
    filename=StringField("filename",validators=[DataRequired()])
    text = TextAreaField("write here",validators=[DataRequired()])
    submit = SubmitField('Done')


class EditForm(FlaskForm):
    filename=StringField("filename",validators=[DataRequired()])
    text = TextAreaField("write here",validators=[DataRequired()])
    submit = SubmitField('Done')

class ResetForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField("email",validators=[DataRequired(), Email()])
    submit = SubmitField('GET')

class EmailForm(FlaskForm):
    email = StringField("email",validators=[DataRequired(), Email()])
    submit = SubmitField('SEND')


class FindForm(FlaskForm):
    user = StringField("search user",validators=[DataRequired()])
    submit = SubmitField('SEND')

class SaveForm(FlaskForm):
    filename = StringField("rename",validators=[DataRequired()])
    submit = SubmitField('save')
