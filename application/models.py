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
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

subjectTeacherAssociation = db.Table('subject-teacher association', db.Column('subjectId', db.Integer, db.ForeignKey('subject.id')), db.Column('teacherId', db.Integer, db.ForeignKey('teacher.id')))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    teachers = db.relationship('Teacher', secondary=subjectTeacherAssociation, backref=db.backref('subjects', lazy = 'dynamic'))
    classITA = db.Column(db.String(20), nullable=False)

    def __init__(self, id, code, name, classITA):
        self.id = id
        self.code = code
        self.name = name
        self.classITA = classITA

    def __repr__(self):
        return f"Subject('{self.code}', '{self.name}')"

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routeIdentifier = db.Column(db.String(50), unique = True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    room = db.Column(db.String(120), nullable=False)
    ramal = db.Column(db.Integer, nullable=False)

    def __init__(self, id, routeIdentifier, name, email, room, ramal):
        self.id = id
        self.routeIdentifier = routeIdentifier
        self.name = name
        self.email = email
        self.room = room
        self.ramal = ramal

    def __repr__(self):
        return f"Teacher('{self.title}', '{self.name}', '{self.subjects}')"
