from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Name',
               validators=[DataRequired(), Length(min=4, max=120)])
    email = StringField('Email',
            validators=[DataRequired(), Email()])
    classITA = StringField('Turma', validators=[DataRequired()])
    isRepr = BooleanField('Representante de turma')
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha',
                         validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Cadastre-se')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Esse email já está sendo utilizado. Escolha outro.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Login')