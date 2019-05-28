#coding: utf-8

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application.models import User


class RegistrationForm(FlaskForm):
    choices = [('COMP19','COMP-19'),('AER19','AER-19'),('AESP19','AESP-19'),('ELE19','ELE-19'),('CIVIL19','CIVIL-19'),('MEC19','MEC-19'),
    ('COMP20','COMP-20'),('AER20','AER-20'),('AESP20','AESP-20'),('ELE20','ELE-20'),('CIVIL20','CIVIL-20'),('MEC20','MEC-20'),
    ('COMP21','COMP-21'),('AER21','AER-21'),('AESP21','AESP-21'),('ELE20','ELE-21'),('CIVIL21','CIVIL-21'),('MEC21','MEC-21'),
    ('FUND22','FUND-22'),('FUND23','FUND-23')]
    name = StringField('Nome',
               validators=[DataRequired(), Length(min=4, max=120)])
    email = StringField('Email',
            validators=[DataRequired(), Email()])
    classITA = SelectField('Turma', choices=choices ,validators=[DataRequired()])
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
