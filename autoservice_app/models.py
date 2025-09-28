from datetime import datetime
from . import db

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    phone = db.Column(db.String(20), unique=True, nullable=False)

    cars = db.relationship('Car', backref='owner', lazy=True)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)

    requests = db.relationship('ServiceRequest', backref='car', lazy=True)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    request_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    issues = db.Column(db.Text, nullable=False)

    repairs = db.relationship('Repair', backref='request', lazy=True)


class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completion_date = db.Column(db.Date)

    spare_parts = db.relationship('SparePart', backref='repair', lazy=True)


class SparePart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repair.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    number = db.Column(db.String(64), nullable=False)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.String(64), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.String(64), nullable=False)
    bonus = db.Column(db.Float, default=0.0)
