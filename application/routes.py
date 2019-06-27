#coding: utf-8

from flask import render_template, redirect, url_for, flash
from flask import request
from application import app, bcrypt, db
from application.forms import RegistrationForm, LoginForm, TeacherSearchForm, SubjectSearchForm, RateSubjectForm, ActivityForm, AcceptForm
from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import StringField
from flask_login import login_user, current_user, logout_user, login_required
from application.models import User, Teacher, Subject, RatingElectiveSubject, Activity, Absence, CalendarMonths
from contextlib import contextmanager
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

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
            abs = Absence(student=current_user,subject=subject,abs=0.0,just=0)
            db.session.add(abs)
            db.session.flush()
            db.session.commit()
            flash(subjectCode + ' foi adicionada às suas \"Disciplinas em curso\".', 'success')
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
            abs = Absence(student=user,subject=subject,abs=0.0,just=0)
            db.session.add(abs)

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
        else:
            flash('Digite o nome do professor na ferramenta de busca para visualizar suas informações.', 'warning')
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

def computeNewAverageValues(ratings,formCoursewareData, formTeacherRateData, formFinalRate, formEvaluationMethodData, notEditing):
    averages = []
    averages.append(0)
    averages.append(0)
    averages.append(0)
    averages.append(0)

    if notEditing:
        for rating in ratings:
            averages[0] += rating.courseware
            averages[1] += rating.teacherRate
            averages[2] += rating.finalRate
            averages[3] += rating.evaluationMethod
    else:
        for rating in ratings:
            if rating.raterId != current_user.id:
                averages[0] += rating.courseware
                averages[1] += rating.teacherRate
                averages[2] += rating.finalRate
                averages[3] += rating.evaluationMethod

    averages[0] = (averages[0] + int(formCoursewareData))/(len(ratings) + notEditing)
    averages[1] = (averages[1] + int(formTeacherRateData))/(len(ratings) + notEditing)
    averages[2] = (averages[2] + formFinalRate)/(len(ratings) + notEditing)
    averages[3] = (averages[3] + int(formEvaluationMethodData))/(len(ratings) + notEditing)
    return averages

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
            previousRatings = RatingElectiveSubject.query.filter_by(subjectId=subjId).all()
            finalRate = int(form.courseware.data)*(0.2) + int(form.teacherRate.data)*(0.5) + int(form.evaluationMethod.data)*(0.3)
            newAverages = computeNewAverageValues(previousRatings,form.courseware.data, form.teacherRate.data, finalRate , form.evaluationMethod.data, 1)

            subject.coursewareRate = newAverages[0]
            subject.teachersRate = newAverages[1]
            subject.finalRate = newAverages[2]
            subject.evaluationMethodRate = newAverages[3]
            subject.numberOfRatings = subject.numberOfRatings + 1

            rating = RatingElectiveSubject(subject, current_user, form.anonymous.data, form.courseware.data, form.teacherRate.data, form.evaluationMethod.data, form.comment.data, finalRate)
            db.session.add(rating)
            db.session.commit()
            flash('Sua avaliação foi adicionada! Muito obrigado pela contribuição.', 'success')
            return redirect(url_for('rateSubjects'))
        return render_template('ratingsubjects.html', subject=subject, teachers=teachers, form=form, title='Nova avaliação de disciplina eletiva')
    return redirect(url_for('login'))

def showAllSubjectsRated(subjectsAux):
    subjects = []
    for subject in subjectsAux:
        if subject.numberOfRatings > 0:
            subjects.append(subject)
    return subjects

@app.route("/searchratedsubjects", defaults={'orderBy': None}, methods=['GET', 'POST'])
@app.route("/searchratedsubjects/<orderBy>", methods=['GET', 'POST'])
def searchRatedSubjects(orderBy):
    if current_user.is_authenticated:
        form = SubjectSearchForm()
        subjects = []
        order = 'finalRate'
        if form.validate_on_submit():
            if form.typeOfSearch.data == 'name':
                subjectsAux = Subject.query.filter(Subject.name.contains(form.subject.data)).all()
            elif form.typeOfSearch.data == 'code':
                subjectsAux = Subject.query.filter(Subject.code.contains(form.subject.data)).all()
            # else:
                # subjectsAux = Subject.query.filter(Subject.teachers.contains(form.subject.data)).all()
            if subjectsAux:
                subjects = showAllSubjectsRated(subjectsAux)
                if not subjects:
                    flash('Você já avaliou ou está cursando todas as disciplinas encontradas com a palavra-chave buscada.', 'warning')
            else:
                flash('Disciplina não foi encontrada ou não é eletiva.', 'danger')
        else:
            if orderBy:
                if orderBy == 'finalRate':
                    subjectsAux = Subject.query.order_by(Subject.finalRate.desc()).all()
                elif orderBy == 'teacherRate':
                    subjectsAux = Subject.query.order_by(Subject.teachersRate.desc()).all()
                    order = 'teacherRate'
                elif orderBy == 'coursewareRate':
                    subjectsAux = Subject.query.order_by(Subject.coursewareRate.desc()).all()
                    order = 'coursewareRate'
                elif orderBy == 'evaluationMethodRate':
                    subjectsAux = Subject.query.order_by(Subject.evaluationMethodRate.desc()).all()
                    order = 'evaluationMethodRate'
            else:
                subjectsAux = Subject.query.all()
            subjects = showAllSubjectsRated(subjectsAux)

        return render_template('searchratedsubjects.html', subjects=subjects, form=form, round=round, order=order)
    else:
        return redirect(url_for('login'))

@app.route("/gettingRatingInfo/<subjId>", methods=['GET', 'POST'])
def gettingRatingInfo(subjId):
    if current_user.is_authenticated:
        if subjId:
            subject = Subject.query.filter_by(id=subjId).first()
            teachers = ""
            for teacher in subject.teachers:
                if teachers != "":
                    teachers = teachers + ", "
                teachers = teachers + "Prof. " + teacher.name
            ratings = RatingElectiveSubject.query.filter_by(subjectId=subjId).all()
            comments = []
            for rating in ratings:
                if rating.anonymous == True:
                    name = "Comentário anônimo:"
                    text = rating.comment
                else:
                    rater = User.query.filter_by(id=rating.raterId).first()
                    name = rater.name + ":"
                    text = rating.comment
                comment = [name, text]
                comments.append(comment)


        return render_template('electivesubjectrate.html', subject=subject, teachers=teachers, comments=comments, round=round)
    return redirect(url_for('login'))


@app.route("/activities", methods=['GET', 'POST'])
def activities():
    if current_user.is_authenticated:
        activities = Activity.query.filter_by(owner=current_user, status='Ativo').all()
        if not activities:
            flash('Você não possui atividades ativas no momento.', 'warning')
        return render_template('activities.html',activities=activities)
    else:
        return redirect(url_for('login'))

@app.route("/activities/new", methods=['GET', 'POST'])
def new_activity():
    if current_user.is_authenticated:
        form = ActivityForm()
        if request.method == 'GET':
            form.date_due.data = date.today()
        if form.validate_on_submit():
            if form.forClass_n_quest.data and form.forClass_quest.data:
                flash('Você não pode marcar as duas opções', 'danger')
                return redirect(url_for('activities'))
            if form.forClass_n_quest.data or form.forClass_quest.data:
                users = User.query.filter_by(classITA=current_user.classITA).all()
                for user in users:
                    status = ('Pendente' if form.forClass_quest.data else 'Ativo')
                    activity = Activity(title=form.title.data, content=form.content.data, date_due=form.date_due.data, priority=form.priority.data, forClass_quest=form.forClass_quest.data, forClass_n_quest= form.forClass_n_quest.data, status=status, progress=form.progress.data, owner=user)
                    db.session.add(activity)
            else:
                activity = Activity(title=form.title.data, content=form.content.data, date_due=form.date_due.data, priority=form.priority.data, forClass_quest=form.forClass_quest.data, forClass_n_quest= form.forClass_n_quest.data, status='Ativo', progress=form.progress.data, owner=current_user)
                db.session.add(activity)
            flash('Atividade criada com sucesso!', 'success')
            db.session.commit()
            return redirect(url_for('activities'))
        return render_template('new_activity.html', form=form, title='Nova Atividade')
    else:
        return redirect(url_for('login'))

@app.route("/activities/<int:act_id>/delete", methods=['POST', 'GET'])
def delete_act(act_id):
    if current_user.is_authenticated:
        activity = Activity.query.get(act_id)
        if activity.forClass_quest or activity.forClass_n_quest:
            users = User.query.filter_by(classITA=current_user.classITA).all()
            for user in users:
                activity_d = Activity.query.filter_by(title=activity.title, content=activity.content, date_due=activity.date_due, priority=activity.priority, forClass_quest=activity.forClass_quest, forClass_n_quest=activity.forClass_n_quest, owner=user).first()
                if activity_d:
                    db.session.delete(activity_d)
        else:
            db.session.delete(activity)
        db.session.commit()
        flash('Atividade apagada com sucesso!', 'success')
        return redirect(url_for('activities'))
    else:
        return redirect(url_for('login'))

@app.route("/activities/<int:act_id>/update", methods=['POST', 'GET'])
def update_act(act_id):
    if current_user.is_authenticated:
        activity = Activity.query.get(act_id)
        form = ActivityForm()
        if form.validate_on_submit():
            if form.forClass_n_quest.data and form.forClass_quest.data:
                flash('Você não pode marcar as duas opções', 'danger')
                return redirect(url_for('activities'))
            if form.forClass_quest.data or form.forClass_n_quest.data:
                users = User.query.filter_by(classITA=current_user.classITA).all()
                for user in users:
                    if user.id is not current_user.id:
                        activity_u = Activity.query.filter_by(title=activity.title, content=activity.content, date_due=activity.date_due, priority=activity.priority, forClass_quest=activity.forClass_quest, forClass_n_quest=activity.forClass_n_quest, user_id=user.id).first()
                        if activity_u:
                            activity_u.title = form.title.data
                            activity_u.content = form.content.data
                            activity_u.date_due = form.date_due.data
                            activity_u.priority = form.priority.data
                            activity_u.forClass_quest = form.forClass_quest.data
                            activity_u.forClass_n_quest = form.forClass_n_quest.data
                            activity_u.status = ('Pendente' if form.forClass_quest.data else 'Ativo')
            activity.title = form.title.data
            activity.content = form.content.data
            activity.date_due = form.date_due.data
            activity.priority = form.priority.data
            activity.forClass_quest = form.forClass_quest.data
            activity.forClass_n_quest = form.forClass_n_quest.data
            activity.progress = form.progress.data
            db.session.commit()
            flash('Atividade alterada com sucesso!', 'success')
            return redirect(url_for('activities'))
        elif request.method == 'GET':
            form.title.data = activity.title
            form.content.data = activity.content
            form.date_due.data = activity.date_due
            form.priority.data = activity.priority
            form.forClass_quest.data = activity.forClass_quest
            form.forClass_n_quest.data = activity.forClass_n_quest
            form.progress.data = activity.progress
        return render_template('new_activity.html', form=form, title='Alterar Atividade')
    else:
        return redirect(url_for('login'))

@app.route("/activities/<int:act_id>/update_prog", methods=['POST', 'GET'])
def update_prog(act_id):
    if current_user.is_authenticated:
        activity = Activity.query.get(act_id)
        form = ActivityForm()
        if request.method == 'POST':
            activity.progress = form.progress.data
            db.session.commit()
            flash('Progresso alterado com sucesso!', 'success')
            return redirect(url_for('activities'))
        elif request.method == 'GET':
            form.title.data = activity.title
            form.content.data = activity.content
            form.date_due.data = activity.date_due
            form.priority.data = activity.priority
            form.forClass_quest.data = activity.forClass_quest
            form.forClass_n_quest.data = activity.forClass_n_quest
            form.progress.data = activity.progress
        return render_template('update_progress.html', form=form, title='Alterar Progresso')
    else:
        return redirect(url_for('login'))

@app.route("/activities/<int:act_id>/done_act", methods=['POST', 'GET'])
def done_act(act_id):
    if current_user.is_authenticated:
        activity = Activity.query.get(act_id)
        db.session.delete(activity)
        db.session.commit()
        flash('Atividade feita com sucesso!', 'success')
        return redirect(url_for('activities'))
    else:
        return redirect(url_for('login'))

@app.route("/activities_p", methods=['GET', 'POST'])
def activities_p():
    if current_user.is_authenticated:
        activities = Activity.query.filter_by(owner=current_user, status='Pendente').all()
        if not activities:
            flash('Você não possui atividades a confirmar no momento.', 'warning')
        return render_template('activities_p.html',activities=activities)
    else:
        return redirect(url_for('login'))


@app.route("/activities_p/<int:act_id>/accept", methods=['POST', 'GET'])
def accept_act(act_id):
    if current_user.is_authenticated:
        form = AcceptForm()
        activity = Activity.query.get(act_id)
        if form.validate_on_submit():
            if form.accept.data:
                users = User.query.filter_by(classITA=current_user.classITA).all()
                for user in users:
                    activity_u = Activity.query.filter_by(title=activity.title, content=activity.content, date_due=activity.date_due, priority=activity.priority, forClass_quest=activity.forClass_quest, forClass_n_quest=activity.forClass_n_quest, owner=user).first()
                    activity_u.votes_up += 1
                    if activity_u.votes_up >= 0.5*len(users):
                        activity_u.status = 'Ativo'
            activity.resp_quest = True
            db.session.commit()
            flash('Obrigada pela sua contribuição.', 'success')
            return redirect(url_for('activities'))
        return render_template('accept_quest.html', form=form, activity=activity, title='Questionário de aceitação')
    else:
        return redirect(url_for('login'))

@app.route("/absences", methods=['POST', 'GET'])
def absences():
    if current_user.is_authenticated:
        subjects = current_user.subjects
        return render_template('absences.html', subjects=subjects, Absence=Absence, round=round)
    else:
        return redirect(url_for('login'))

@app.route("/absences/<int:abs_id>/update", methods=['POST', 'GET'])
def update_abs(abs_id):
    if current_user.is_authenticated:
        absence = Absence.query.get(abs_id)
        subject = absence.subject
        return render_template('update_absences.html', absence=absence, subject=subject, round=round)
    else:
        return redirect(url_for('login'))

@app.route("/absences/<int:abs_id>/update/<route>", methods=['POST', 'GET'])
def upd_abs(abs_id,route):
    if current_user.is_authenticated:
        absence = Absence.query.get(abs_id)
        if route == 'AddAtr':
            absence.abs += 0.5
        elif route == 'AddFalt':
            absence.abs += 1
        elif route == 'AddJust':
            absence.just += 1
        elif route == 'RemAtr':
            if absence.abs < 0.5:
                flash('Não há atrasos para serem removidos.', 'warning')
                return redirect(url_for('absences'))
            else:
                absence.abs -= 0.5
        elif route == 'RemFalt':
            if absence.abs < 1:
                flash('Não há faltas para serem removidas.', 'warning')
                return redirect(url_for('absences'))
            else:
                absence.abs -= 1
        elif route == 'RemJust':
            if absence.just < 1:
                flash('Não há justificativas para serem removidas.', 'warning')
                return redirect(url_for('absences'))
            else:
                absence.just -= 1
        db.session.commit()
        flash('Alterações feitas com sucesso!', 'success')
        return redirect(url_for('update_abs', abs_id=abs_id))
    else:
        return redirect(url_for('login'))

def showAllSubjectsUserRated(subjectsAux):
    subjects = []
    for subject in subjectsAux:
        ratings = subject.ratings
        foundUser = False
        for rating in ratings:
            if rating.raterId == current_user.id:
                foundUser = True
                break
        if foundUser:
            subjects.append(subject)
    return subjects

@app.route("/editratedsubjects", methods=['GET', 'POST'])
def editRatedSubjects():
    if current_user.is_authenticated:
        form = SubjectSearchForm()
        subjects = []
        if form.validate_on_submit():
            if form.typeOfSearch.data == 'name':
                subjectsAux = Subject.query.filter(and_(Subject.name.contains(form.subject.data), Subject.numberOfRatings>0)).all()
            elif form.typeOfSearch.data == 'code':
                subjectsAux = Subject.query.filter(and_(Subject.code.contains(form.subject.data), Subject.numberOfRatings>0)).all()
            # else:
                # subjectsAux = Subject.query.filter(Subject.teachers.contains(form.subject.data)).all()
            if subjectsAux:
                subjects = showAllSubjectsUserRated(subjectsAux)
                if not subjects:
                    flash('Você já avaliou ou está cursando todas as disciplinas encontradas com a palavra-chave buscada.', 'warning')
            else:
                flash('Disciplina não foi encontrada ou não é eletiva.', 'danger')
        else:
            subjectsAux = Subject.query.all()
            subjects = showAllSubjectsUserRated(subjectsAux)
        if not subjects:
            flash('Você não realizou avaliações para poder editá-las. Aproveite e faça sua primeira avaliação!', 'warning')

        return render_template('searchalreadyratedsubjects.html', subjects=subjects, form=form)
    else:
        return redirect(url_for('login'))

@app.route("/editingratedsubjects/<int:subjId>", methods=['POST', 'GET'])
def editingRatedSubjects(subjId):
    if current_user.is_authenticated:
        subject = Subject.query.filter_by(id=subjId).first()

        ratings = subject.ratings
        for rat in ratings:
            if rat.raterId == current_user.id:
                ratingId = rat.id
                break

        rating = RatingElectiveSubject.query.get(ratingId)

        teachers = ""
        for teacher in subject.teachers:
            if teachers != "":
                teachers = teachers + ", "
            teachers = teachers + "Prof. " + teacher.name

        form = RateSubjectForm()
        if request.method == 'POST':
            previousRatings = RatingElectiveSubject.query.filter_by(subjectId=subjId).all()
            finalRate = float(form.courseware.data)*(0.2) + float(form.teacherRate.data)*(0.5) + float(form.evaluationMethod.data)*(0.3)

            newAverages = computeNewAverageValues(previousRatings,form.courseware.data, form.teacherRate.data, finalRate , form.evaluationMethod.data, 0)
            subject.coursewareRate = newAverages[0]
            subject.teachersRate = newAverages[1]
            subject.finalRate = newAverages[2]
            subject.evaluationMethodRate = newAverages[3]

            rating.courseware = form.courseware.data
            rating.anonymous = form.anonymous.data
            rating.teacherRate = form.teacherRate.data
            rating.finalRate = finalRate
            rating.evaluationMethod = form.evaluationMethod.data
            rating.comment = form.comment.data

            db.session.add(rating)
            db.session.commit()
            flash('Avaliação alterada com sucesso!', 'success')
            return redirect(url_for('editRatedSubjects'))
        elif request.method == 'GET':
            form.courseware.data = rating.courseware
            form.anonymous.data = rating.anonymous
            form.teacherRate.data = rating.teacherRate
            form.evaluationMethod.data = rating.evaluationMethod
            form.comment.data = rating.comment
        return render_template('ratingsubjects.html', subject=subject, teachers=teachers, form=form, title='Editar avaliação')
    else:
        return redirect(url_for('login'))


def processCellData(monthToDisplay):
    mon = CalendarMonths.query.filter_by(month=monthToDisplay).first()
    cell = []
    currDate = mon.dateToStart
    numberOfCells = 6*7
    for i in range(0, numberOfCells):
        info = []
        info.append(str(currDate.day))
        info.append(currDate.month)
        activities = Activity.query.filter_by(user_id=current_user.id, date_due=currDate, status='Ativo').order_by(Activity.priority.desc()).all()
        for activity in activities:
            info.append(activity.title)
        currDate += timedelta(days=1)
        cell.append(info)
    return cell

@app.route("/calendar", defaults={'month': None}, methods=['GET', 'POST'])
@app.route("/calendar/<int:month>", methods=['GET', 'POST'])
def calendar(month):
    if current_user.is_authenticated:
        if month:
            monthToDisplay = month
        else:
            today = date.today()
            monthToDisplay = today.month

        if monthToDisplay == 1:
            monthName = 'Janeiro 2019'
        elif monthToDisplay == 2:
            monthName = 'Fevereiro 2019'
        elif monthToDisplay == 3:
            monthName = 'Março 2019'
        elif monthToDisplay == 4:
            monthName = 'Abril 2019'
        elif monthToDisplay == 5:
            monthName = 'Maio 2019'
        elif monthToDisplay == 6:
            monthName = 'Junho 2019'
        elif monthToDisplay == 7:
            monthName = 'Julho 2019'
        elif monthToDisplay == 8:
            monthName = 'Agosto 2019'
        elif monthToDisplay == 9:
            monthName = 'Setembro 2019'
        elif monthToDisplay == 10:
            monthName = 'Outubro 2019'
        elif monthToDisplay == 11:
            monthName = 'Novembro 2019'
        else:
            monthName = 'Dezembro 2019'

        cells = processCellData(monthToDisplay)

        return render_template('calendar.html', cells=cells, len=len, monthName=monthName, monthNumber=monthToDisplay)
    else:
        return redirect(url_for('login'))

@app.route("/editingratedsubjects/<int:subjId>/delete", methods=['POST', 'GET'])
def deletingRatedSubjects(subjId):
    if current_user.is_authenticated:
        subject = Subject.query.get(subjId)

        ratings = subject.ratings
        for rat in ratings:
            if rat.raterId == current_user.id:
                ratingId = rat.id
                break

        rating = RatingElectiveSubject.query.get(ratingId)
        db.session.delete(rating)
        subject.numberOfRatings -= 1
        db.session.commit()

        previousRatings = RatingElectiveSubject.query.filter_by(subjectId=subjId).all()

        if len(previousRatings) is not 0:
            newAverages = computeNewAverageValues(previousRatings,0, 0, 0, 0, 0)

            subject.coursewareRate = newAverages[0]
            subject.teachersRate = newAverages[1]
            subject.finalRate = newAverages[2]
            subject.evaluationMethodRate = newAverages[3]
        else:
            subject.coursewareRate = 0
            subject.teachersRate = 0
            subject.finalRate = 0
            subject.evaluationMethodRate = 0
        db.session.commit()
        flash('Avaliação excluída com sucesso!', 'success')
        return redirect(url_for('editRatedSubjects'))
    else:
        return redirect(url_for('login'))
