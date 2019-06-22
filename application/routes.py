#coding: utf-8

from flask import render_template, redirect, url_for, flash
from flask import request
from application import app, bcrypt, db
from application.forms import RegistrationForm, LoginForm, TeacherSearchForm, SubjectSearchForm, RateSubjectForm
from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import StringField
from flask_login import login_user, current_user, logout_user, login_required
from application.models import User, Teacher, Subject, RatingElectiveSubject
from contextlib import contextmanager

@app.route("/")
@app.route("/home")
@app.route("/subjects", methods=['GET'])
def home():
    if current_user.is_authenticated:
        subjects = current_user.subjects
        return render_template('subjects.html', subjects=subjects)
    else:
        return redirect(url_for('login'))

@app.route("/removesubjects", methods = ["GET", "POST"] )
def removeSubjects():
    if current_user.is_authenticated:
        if request.method == "POST":
            subjectsToRemove = request.form.getlist("subjectToRemove")
            if subjectsToRemove:
                for sub in subjectsToRemove:
                    subject = Subject.query.filter_by(id=sub).first()
                    subject.students.remove(current_user)
                    db.session.flush()
                    db.session.commit()
            else:
                flash('É preciso selecionar uma disciplina para removê-la.', 'danger')
            return redirect(url_for('editSubjects'))
    else:
        return redirect(url_for('login'))

@app.route("/editsubjects", methods=['GET'])
def editSubjects():
    if current_user.is_authenticated:
        subjects = current_user.subjects
        return render_template('editsubjects.html', subjects=subjects)
    else:
        return redirect(url_for('login'))

def showAllSubjectsButTheOnesUserIsFollowing(subjectsAux):
    subjects = []
    for subject in subjectsAux:
        foundUser = False
        for student in subject.students:
            if student.id == current_user.id:
                foundUser = True
                break
        if not foundUser:
            subjects.append(subject)
    return subjects

@app.route("/addsubjects", methods=['GET', 'POST'])
def addSubjects():
    if current_user.is_authenticated:
        form = SubjectSearchForm()
        subjects = []
        if form.validate_on_submit():
            if form.typeOfSearch.data == 'name':
                subjectsAux = Subject.query.filter(Subject.name.contains(form.subject.data)).all()
            elif form.typeOfSearch.data == 'code':
                subjectsAux = Subject.query.filter(Subject.code.contains(form.subject.data)).all()
            # else:
                # subjectsAux = Subject.query.filter(Subject.teachers.contains(form.subject.data)).all()
            if subjectsAux:
                subjects = showAllSubjectsButTheOnesUserIsFollowing(subjectsAux)
                if not subjects:
                    flash('Você está cursando todas as disciplinas encontradas com a palavra-chave buscada.', 'warning')
            else:
                flash('Disciplina não encontrada.', 'danger')
            return render_template('addsubjects.html', subjects=subjects, form=form)
        else:
            subjectsAux = Subject.query.all()
            subjects = showAllSubjectsButTheOnesUserIsFollowing(subjectsAux)
            if not subjects:
                flash('Você está cursando todas as disciplinas encontradas com a palavra-chave buscada.', 'warning')
            return render_template('addsubjects.html', subjects=subjects, form=form)
    else:
        return redirect(url_for('login'))

@app.route("/addingsubjects", defaults={'subjectCode': None})
@app.route("/addingsubjects/<subjectCode>", methods=['GET', 'POST'])
def addingSubjects(subjectCode):
    if current_user.is_authenticated:
        if subjectCode:
            subject = Subject.query.filter_by(code=subjectCode).first()
            subject.students.append(current_user)
            db.session.flush()
            db.session.commit()
            flash(subjectCode + ' foi adicionada às suas \"Disciplina em curso\".', 'success')
        else:
            flash('Um erro ocorreu, por favor tente novamente.', 'danger')
        return redirect(url_for('addSubjects'))
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
        db.session.flush()
        db.session.commit()
        flash('Sua conta foi criada! Agora você pode ingressar no sistema.', 'success')
        return redirect(url_for('login'))
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
                flash('Login não realizado. Por favor verifique seu email e senha.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/teacher", defaults={'routeIdentifier': None}, methods=['GET', 'POST'])
@app.route("/teacher/<routeIdentifier>", methods=['GET', 'POST'])
def teacher(routeIdentifier):
    if current_user.is_authenticated:
        form = TeacherSearchForm()
        if form.validate_on_submit():
            teachers = Teacher.query.filter(Teacher.name.contains(form.teacher.data)).all()
            if teachers:
                return render_template('chooseteacher.html', teachers=teachers, form=form)
            else:
                flash('Professor não encontrado.', 'danger')
                return render_template('teacher.html', teacher=None, subjects=None, form=form)
        if routeIdentifier:
            teacher = Teacher.query.filter_by(routeIdentifier=routeIdentifier).first_or_404(description='There is no data with the route identifier {}'.format(routeIdentifier))

            subjects = ""
            for subject in teacher.subjects:
                if subjects != "":
                    subjects = subjects + ", "
                subjects = subjects + subject.code

            return render_template('teacher.html', teacher=teacher, subjects=subjects, form=form)

        return render_template('teacher.html', teacher=None, subjects=None, form=form)
    return redirect(url_for('login'))

def showAllSubjectsButTheOnesUserHasRatedOrIsFollowing(subjectsAux):
    subjects = []
    for subject in subjectsAux:
        if subject.classITA == 'Eletiva':
            foundUser = False
            for rating in subject.ratings:
                if rating.raterId == current_user.id:
                    foundUser = True
                    break
            if not foundUser:
                for student in subject.students:
                    if student.id == current_user.id:
                        foundUser = True
                        break
                if not foundUser:
                    subjects.append(subject)
    return subjects

@app.route("/ratesubjects", methods=['GET', 'POST'])
def rateSubjects():
    if current_user.is_authenticated:
        form = SubjectSearchForm()
        subjects = []
        if form.validate_on_submit():
            if form.typeOfSearch.data == 'name':
                subjectsAux = Subject.query.filter(Subject.name.contains(form.subject.data)).all()
            elif form.typeOfSearch.data == 'code':
                subjectsAux = Subject.query.filter(Subject.code.contains(form.subject.data)).all()
            # else:
                # subjectsAux = Subject.query.filter(Subject.teachers.contains(form.subject.data)).all()
            if subjectsAux:
                subjects = showAllSubjectsButTheOnesUserHasRatedOrIsFollowing(subjectsAux)
                if not subjects:
                    flash('Você já avaliou ou está cursando todas as disciplinas encontradas com a palavra-chave buscada.', 'warning')
            else:
                flash('Disciplina não foi encontrada ou não é eletiva.', 'danger')
        else:
            subjectsAux = Subject.query.all()
            subjects = showAllSubjectsButTheOnesUserHasRatedOrIsFollowing(subjectsAux)
        return render_template('choosesubjecttorate.html', subjects=subjects, form=form)
    else:
        return redirect(url_for('login'))

@app.route("/ratingsubjects", defaults={'subjId': None})
@app.route("/ratingsubjects/<subjId>", methods=['GET', 'POST'])
def ratingSubjects(subjId):
    if current_user.is_authenticated:
        if subjId:
            subject = Subject.query.filter_by(id=subjId).first()
            teachers = ""
            for teacher in subject.teachers:
                if teachers != "":
                    teachers = teachers + ", "
                teachers = teachers + "Prof. " + teacher.name
        form = RateSubjectForm()
        if form.validate_on_submit():
            rating = RatingElectiveSubject(subject, current_user, form.anonymous.data, form.courseware.data, form.teacherRate.data, form.evaluationMethod.data, form.comment.data)
            db.session.add(rating)
            db.session.flush()
            db.session.commit()
            flash('Sua avaliação foi adicionada! Muito obrigado pela contribuição.', 'success')
            return redirect(url_for('rateSubjects'))
        return render_template('ratingsubjects.html', subject=subject, teachers=teachers, form=form)
    return redirect(url_for('login'))
