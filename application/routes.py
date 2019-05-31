#coding: utf-8

from flask import render_template, redirect, url_for, flash
from application import app, bcrypt, db
from application.forms import RegistrationForm, LoginForm, SearchForm
from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import StringField
from flask_login import login_user, current_user, logout_user, login_required
from application.models import User, Teacher, Subject

@app.route("/")
@app.route("/home")
@app.route("/subjects")
def home():
    if current_user.is_authenticated:
        subjects = Subject.query.filter(Subject.students.any(User.id.in_([student.id for student in current_user.subjects]))).all()
        return render_template('subjects.html', subjects=subjects)
    else:
        return redirect(url_for('login'))

@app.route("/cadastro", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password, classITA=form.classITA.data, isRepr=form.isRepr.data)
        db.session.add(user)

        for subject in Subject.query.filter_by(classITA=user.classITA).all():
            user.subjects.append(subject)
        db.session.commit()
        flash('Sua conta foi criada! Agora você pode ingressar no sistema.', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Cadastro', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
            else:
                flash('Login não realizado. Por favor verifique seu email e senha', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/teacher", defaults={'routeIdentifier': None})
@app.route("/teacher/<routeIdentifier>", methods=['GET'])
def teacher(routeIdentifier):
    if current_user.is_authenticated:
        if routeIdentifier:
            teacher = Teacher.query.filter_by(routeIdentifier=routeIdentifier).first_or_404(description='There is no data with the route identifier {}'.format(routeIdentifier))

            subjects = ""
            for subject in teacher.subjects:
                if subjects != "":
                    subjects = subjects + ", "
                subjects = subjects + subject.code

            return render_template('teacher.html', teacher=teacher, subjects=subjects)
        else:
            return render_template('teacher.html', teacher=None, subjects=None)
    else:
        return redirect(url_for('login'))

@app.route("/teacher/search", methods=['GET', 'POST'])
def teacherSearch():
    if current_user.is_authenticated:
        form = SearchForm()
        teacher = Teacher.query.filter(Teacher.name.contains(form.search.data)).first()
        if teacher:
            subjects = ""
            for subject in teacher.subjects:
                if subjects != "":
                    subjects = subjects + ", "
                subjects = subjects + subject.code

            return render_template('teacher.html', teacher=teacher, subjects=subjects)
        else:
            flash('Professor não encontrado!', 'danger')
            return redirect(url_for('teacher'))
