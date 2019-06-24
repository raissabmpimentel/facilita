#coding: utf-8

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from application.models import User

class RegistrationForm(FlaskForm):
    choices = [('COMP19','COMP-19'),('AER19','AER-19'),('AESP19','AESP-19'),('ELE19','ELE-19'),('CIVIL19','CIVIL-19'),('MEC19','MEC-19'),
    ('COMP20','COMP-20'),('AER20','AER-20'),('AESP20','AESP-20'),('ELE20','ELE-20'),('CIVIL20','CIVIL-20'),('MEC20','MEC-20'),
    ('COMP21','COMP-21'),('AER21','AER-21'),('AESP21','AESP-21'),('ELE20','ELE-21'),('CIVIL21','CIVIL-21'),('MEC21','MEC-21'),
    ('FUND221','FUND-22.1'),('FUND222','FUND-22.2'), ('FUND223','FUND-22.3'), ('FUND224','FUND-22.4'),
    ('FUND231','FUND-23.1'),('FUND232','FUND-23.2'), ('FUND233','FUND-23.3'), ('FUND234','FUND-23.4')]
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

class TeacherSearchForm(FlaskForm):
    teacher = StringField('Nome do professor', validators=[DataRequired()], render_kw={"placeholder": "Digite o nome do professor"})
    submit = SubmitField('Buscar')

class SubjectSearchForm(FlaskForm):
    #choices = [('name', 'Nome da disciplina'), ('code', 'Sigla da disciplina'), ('teacher', 'Nome do professor')]
    choices = [('name', 'Nome da disciplina'), ('code', 'Sigla da disciplina')]
    typeOfSearch = SelectField('Tipo de Busca', choices=choices, validators=[DataRequired()])
    subject = StringField('Nome da disciplina', validators=[DataRequired()], render_kw={"placeholder": "Digite o nome da disciplina"})
    submit = SubmitField('Buscar')

class AddSubjectForm(FlaskForm):
    subject = StringField('Nome da disciplina')
    submit = SubmitField('Buscar')

class RateSubjectForm(FlaskForm):
    choices = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    courseware = SelectField('Material Didático disponibilizado pelo professor:', choices=choices, validators=[DataRequired()])
    teacherRate = SelectField('Didática do professor:', choices=choices, validators=[DataRequired()])
    evaluationMethod = SelectField('Método avaliativo da disciplina:', choices=choices, validators=[DataRequired()])
    anonymous = BooleanField('Desejo que esta avaliação seja anônima')
    comment = StringField('Comentário', validators=[DataRequired()], render_kw={"placeholder": "Conte mais como foi sua experiência cursando a disciplina."})
    submit = SubmitField('Enviar')

class ActivityForm(FlaskForm):
    choices = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    choices_2 = [('Não Iniciada', 'Não Iniciada'), ('Em Progresso', 'Em Progresso')]
    title = StringField('Título', validators=[DataRequired()])
    content = TextAreaField('Comentários')
    date_due = DateField('Data de Entrega', format='%d/%m/%Y', validators=[Optional()])
    priority = SelectField('Prioridade', choices=choices ,validators=[DataRequired()])
    progress = SelectField('Progresso', choices=choices_2 ,validators=[DataRequired()])
    forClass = BooleanField('Aplicar para toda a turma')
    submit = SubmitField('Salvar atividade')
