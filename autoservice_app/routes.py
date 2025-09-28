from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from .models import Owner, Car, Employee, ServiceRequest, Repair, SparePart
from datetime import datetime

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")



# ------------------- Owners -------------------
@bp.route("/owners", methods=["GET", "POST"])
def owners():
    if request.method == "POST":
        owner = Owner(
            last_name=request.form["last_name"],
            first_name=request.form["first_name"],
            middle_name=request.form.get("middle_name"),
            phone=request.form["phone"],
        )
        db.session.add(owner)
        db.session.commit()
        return redirect(url_for("main.owners"))

    owners = Owner.query.all()
    return render_template("owners.html", owners=owners)


# ------------------- Cars -------------------
@bp.route("/cars", methods=["GET", "POST"])
def cars():
    if request.method == "POST":
        car = Car(
            number=request.form["number"],
            brand=request.form["brand"],
            release_date=datetime.strptime(request.form["release_date"], "%Y-%m-%d"),
            owner_id=request.form["owner_id"],
        )
        db.session.add(car)
        db.session.commit()
        return redirect(url_for("main.cars"))

    cars = Car.query.all()
    owners = Owner.query.all()
    return render_template("cars.html", cars=cars, owners=owners)


# ------------------- Employees -------------------
@bp.route("/employees", methods=["GET", "POST"])
def employees():
    if request.method == "POST":
        employee = Employee(
            last_name=request.form["last_name"],
            first_name=request.form["first_name"],
            middle_name=request.form.get("middle_name"),
            birth_date=datetime.strptime(request.form["birth_date"], "%Y-%m-%d"),
            address=request.form["address"],
            phone=request.form["phone"],
            position=request.form["position"],
            salary=float(request.form["salary"]),
            experience=int(request.form["experience"]),
            schedule=request.form["schedule"],
            bonus=float(request.form.get("bonus", 0.0)),
        )
        db.session.add(employee)
        db.session.commit()
        return redirect(url_for("main.employees"))

    employees = Employee.query.all()
    return render_template("employees.html", employees=employees)


# ------------------- Service Requests -------------------
@bp.route("/requests", methods=["GET", "POST"])
def requests():
    if request.method == "POST":
        request_obj = ServiceRequest(
            car_id=request.form["car_id"],
            issues=request.form["issues"],
        )
        db.session.add(request_obj)
        db.session.commit()
        return redirect(url_for("main.requests"))

    requests_ = ServiceRequest.query.all()
    cars = Car.query.all()
    return render_template("requests.html", requests=requests_, cars=cars)


# ------------------- Repairs -------------------
@bp.route("/repairs", methods=["GET", "POST"])
def repairs():
    if request.method == "POST":
        repair = Repair(
            request_id=request.form["request_id"],
            description=request.form["description"],
            completion_date=(
                datetime.strptime(request.form["completion_date"], "%Y-%m-%d")
                if request.form.get("completion_date")
                else None
            ),
        )
        db.session.add(repair)
        db.session.commit()
        return redirect(url_for("main.repairs"))

    repairs = Repair.query.all()
    requests_ = ServiceRequest.query.all()
    return render_template("repairs.html", repairs=repairs, requests=requests_)


# ------------------- Spare Parts -------------------
@bp.route("/spares", methods=["GET", "POST"])
def spares():
    if request.method == "POST":
        spare = SparePart(
            repair_id=request.form["repair_id"],
            name=request.form["name"],
            number=request.form["number"],
        )
        db.session.add(spare)
        db.session.commit()
        return redirect(url_for("main.spares"))

    spares = SparePart.query.all()
    repairs = Repair.query.all()
    return render_template("spares.html", spares=spares, repairs=repairs)
