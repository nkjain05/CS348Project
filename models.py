from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    major = db.Column(db.String(100))
    applications = db.relationship('Application', backref='user', cascade='all, delete')

class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    headquarters = db.Column(db.String(100))

class Status(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50))

class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))
    position_title = db.Column(db.String(100))
    applied_date = db.Column(db.String(10))
    response_date = db.Column(db.String(10))
    link_to_posting = db.Column(db.String(255))

    user = db.relationship('User')
    company = db.relationship('Company')
    status = db.relationship('Status')



