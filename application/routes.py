#coding: utf-8

from flask import render_template, redirect, url_for, flash
from flask import request
from application import app, bcrypt, db
from application.forms import RegistrationForm, LoginForm, TeacherSearchForm, SubjectSearchForm, RateSubjectForm, ActivityForm
from flask_wtf import Form
from wtforms.validators import DataRequired
from wtforms import StringField
from flask_login import login_user, current_user, logout_user, login_required
from application.models import User, Teacher, Subject, RatingElectiveSubject, Activity, Absence
from contextlib import contextmanager
from datetime import date

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

def computeNewAverageValues(ratings,formCoursewareData, formTeacherRateData, formFinalRate, formEvaluationMethodData):
    averages = []
    averages.append(0)
    averages.append(0)
    averages.append(0)
    averages.append(0)
    for rating in ratings:
        averages[0] += rating.courseware
        averages[1] += rating.teacherRate
        averages[2] += rating.finalRate
        averages[3] += rating.evaluationMethod

    averages[0] = (averages[0] + int(formCoursewareData))/(len(ratings) + 1)
    averages[1] = (averages[1] + int(formTeacherRateData))/(len(ratings) + 1)
    averages[2] = (averages[2] + int(formFinalRate))/(len(ratings) + 1)
    averages[3] = (averages[3] + int(formEvaluationMethodData))/(len(ratings) + 1)
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
            newAverages = computeNewAverageValues(previousRatings,form.courseware.data, form.teacherRate.data, finalRate , form.evaluationMethod.data)

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
        return render_template('ratingsubjects.html', subject=subject, teachers=teachers, form=form)
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
                    subjectsAux = Subject.query.order_by(Subject.coursewareRate.desc()).all()
                elif orderBy == 'coursewareRate':
                    subjectsAux = Subject.query.order_by(Subject.teachersRate.desc()).all()
                elif orderBy == 'evaluationMethodRate':
                    subjectsAux = Subject.query.order_by(Subject.evaluationMethodRate.desc()).all()
            else:
                subjectsAux = Subject.query.all()
            subjects = showAllSubjectsRated(subjectsAux)

        return render_template('searchratedsubjects.html', subjects=subjects, form=form)
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


        return render_template('electivesubjectrate.html', subject=subject, teachers=teachers, comments=comments)
    return redirect(url_for('login'))


@app.route("/activities", methods=['GET', 'POST'])
def activities():
    if current_user.is_authenticated:
        activities = Activity.query.filter_by(owner=current_user).all()
        if not activities:
            flash('Você não possui atividades no momento.', 'warning')
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
            if form.forClass.data:
                users = User.query.filter_by(classITA=current_user.classITA).all()
                for user in users:
                    activity = Activity(title=form.title.data, content=form.content.data, date_due=form.date_due.data, priority=form.priority.data, forClass=form.forClass.data, progress=form.progress.data, owner=user)
                    db.session.add(activity)
            else:
                activity = Activity(title=form.title.data, content=form.content.data, date_due=form.date_due.data, priority=form.priority.data, forClass=form.forClass.data, progress=form.progress.data, owner=current_user)
                db.session.add(activity)
            db.session.commit()
            return redirect(url_for('activities'))
        return render_template('new_activity.html', form=form, title='Nova Atividade')
    else:
        return redirect(url_for('login'))

@app.route("/activities/<int:act_id>/delete", methods=['POST', 'GET'])
def delete_act(act_id):
    if current_user.is_authenticated:
        activity = Activity.query.get(act_id)
        if activity.forClass:
            users = User.query.filter_by(classITA=current_user.classITA).all()
            for user in users:
                activity_d = Activity.query.filter_by(title=activity.title, content=activity.content, date_due=activity.date_due, priority=activity.priority, forClass=activity.forClass, owner=user).first()
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
            if form.forClass.data:
                users = User.query.filter_by(classITA=current_user.classITA).all()
                for user in users:
                    activity_u = Activity.query.filter_by(title=activity.title, content=activity.content, date_due=activity.date_due, priority=activity.priority, forClass=activity.forClass, owner=user).first()
                    if activity_u:
                        activity_u.title = form.title.data
                        activity_u.content = form.content.data
                        activity_u.date_due = form.date_due.data
                        activity_u.priority = form.priority.data
            else:
                activity.title = form.title.data
                activity.content = form.content.data
                activity.date_due = form.date_due.data
                activity.priority = form.priority.data
                activity.forClass = form.forClass.data
                activity.progress = form.progress.data
            db.session.commit()
            flash('Atividade alterada com sucesso!', 'success')
            return redirect(url_for('activities'))
        elif request.method == 'GET':
            form.title.data = activity.title
            form.content.data = activity.content
            form.date_due.data = activity.date_due
            form.priority.data = activity.priority
            form.forClass.data = activity.forClass
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
            form.forClass.data = activity.forClass
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

@app.route("/absences", methods=['POST', 'GET'])
def absences():
    if current_user.is_authenticated:
        subjects = current_user.subjects
        return render_template('absences.html', subjects=subjects, Absence=Absence)
    else:
        return redirect(url_for('login'))

@app.route("/absences/<int:abs_id>/update", methods=['POST', 'GET'])
def update_abs(abs_id):
    if current_user.is_authenticated:
        absence = Absence.query.get(abs_id)
        subject = absence.subject
        return render_template('update_absences.html', absence=absence, subject=subject)
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
        return redirect(url_for('absences'))
    else:
        return redirect(url_for('login'))
