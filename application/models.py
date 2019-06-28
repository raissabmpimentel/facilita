from application import db, login_manager, app
from flask_login import UserMixin
from flask_migrate import Migrate

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

subjectStudentAssociation = db.Table('subject-student association', db.Column('subjectId', db.Integer, db.ForeignKey('subject.id')), db.Column('studentId', db.Integer, db.ForeignKey('user.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    classITA = db.Column(db.String(20), nullable=False)
    isRepr = db.Column(db.Boolean, nullable=False)
    subjects = db.relationship('Subject', secondary=subjectStudentAssociation, backref=db.backref('students', lazy = 'dynamic'))
    ratings = db.relationship('RatingElectiveSubject', backref='rater')
    activities = db.relationship('Activity', backref='owner', lazy=True)
    absences = db.relationship('Absence', backref='student', lazy=True)
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

subjectTeacherAssociation = db.Table('subject-teacher association', db.Column('subjectId', db.Integer, db.ForeignKey('subject.id')), db.Column('teacherId', db.Integer, db.ForeignKey('teacher.id')))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    teachers = db.relationship('Teacher', secondary=subjectTeacherAssociation, backref=db.backref('subjects', lazy = 'dynamic'))
    classITA = db.Column(db.String(20), nullable=False)
    lim_abs = db.Column(db.Float, nullable=False)
    ratings = db.relationship('RatingElectiveSubject', backref='subject')
    absences = db.relationship('Absence', backref='subject', lazy=True)
    numberOfRatings = db.Column(db.Integer, nullable=False)
    finalRate = db.Column(db.Float, nullable=False)
    coursewareRate = db.Column(db.Float, nullable=False)
    teachersRate = db.Column(db.Float, nullable=False)
    evaluationMethodRate = db.Column(db.Float, nullable=False)

    def __init__(self, code, name, classITA, numberOfRatings, coursewareRate, teachersRate, evaluationMethodRate, finalRate, lim_abs):
        self.code = code
        self.name = name
        self.classITA = classITA
        self.numberOfRatings = numberOfRatings
        self.coursewareRate = coursewareRate
        self.teachersRate = teachersRate
        self.evaluationMethodRate = evaluationMethodRate
        self.finalRate = finalRate
        self.lim_abs = lim_abs

    def __repr__(self):
        return f"Subject('{self.code}', '{self.name}')"

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routeIdentifier = db.Column(db.String(50), unique = True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    room = db.Column(db.String(120), nullable=False)
    ramal = db.Column(db.Integer, nullable=False)

    def __init__(self, routeIdentifier, name, email, room, ramal):
        self.routeIdentifier = routeIdentifier
        self.name = name
        self.email = email
        self.room = room
        self.ramal = ramal

    def __repr__(self):
        return f"Teacher('{self.title}', '{self.name}', '{self.subjects}')"

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_due = db.Column(db.Date, nullable=True)
    forClass_quest = db.Column(db.Boolean, nullable=False, default=False)
    forClass_n_quest = db.Column(db.Boolean, nullable=False, default=False)
    priority = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    votes_up = db.Column(db.Integer, nullable=False, default=0)
    resp_quest = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Activity('{self.title}' written by {self.user_id})"

class CalendarMonths(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateToStart = db.Column(db.Date, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __init__(self, month, year, dateToStart):
        self.month = month
        self.year = year
        self.dateToStart = dateToStart

    def __repr__(self):
        return f"CalendarMonths('{self.month}' of {self.year} start on {self.dateToStart})"

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    abs = db.Column(db.Float, nullable=False, default=0.0)
    just = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Absences: Total {self.abs} abscences of subject {self.subject_id} of user {self.user_id}"

class RatingElectiveSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))
    raterId = db.Column(db.Integer, db.ForeignKey('user.id'))
    anonymous = db.Column(db.Boolean, nullable=False)
    courseware = db.Column(db.Integer, nullable=False)
    teacherRate = db.Column(db.Integer, nullable=False)
    finalRate = db.Column(db.Integer, nullable=False)
    evaluationMethod = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __init__(self, subject, rater, anonymous, courseware, teacherRate, evaluationMethod, comment):
        self.subject = subject
        self.rater = rater
        self.anonymous = anonymous
        self.courseware = courseware
        self.teacherRate = teacherRate
        self.evaluationMethod = evaluationMethod
        self.comment = comment
        self.finalRate = 0

    def __repr__(self):
        return f"RateElectiveSubject('{self.title}', '{self.subject}', '{self.rater}', '{self.courseware}', '{self.teacherRate}', '{self.evaluationMethod}', '{self.comment}')"
