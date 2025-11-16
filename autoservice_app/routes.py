from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from markupsafe import escape
from datetime import datetime
from . import db
from .models import Owner, Car, Employee, ServiceRequest, Repair, SparePart, CompletedWork, repair_employees
import html
import re

bp = Blueprint("main", __name__)


class SecurityHelper:

    @staticmethod
    def sanitize_input(input_string):
        """Защита от XSS и HTML injection"""
        if input_string is None:
            return ""
        # Экранирование HTML символов
        sanitized = html.escape(str(input_string))
        # Удаление потенциально опасных тегов
        sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+=', '', sanitized, flags=re.IGNORECASE)
        return sanitized

    @staticmethod
    def validate_phone(phone):
        """Валидация номера телефона"""
        if not phone:
            return False
        # Российский формат номеров
        pattern = r'^(\+7|8)[\d\-\(\)\s]{10,15}$'
        return bool(re.match(pattern, str(phone)))

    @staticmethod
    def validate_email(email):
        """Валидация email (если добавите в будущем)"""
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))

    @staticmethod
    def sanitize_sql_identifier(identifier):
        """Защита от SQL injection для идентификаторов"""
        # Разрешаем только буквы, цифры и подчеркивания
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', str(identifier)):
            return identifier
        raise ValueError("Invalid SQL identifier")


class ViewHelper:
    """Класс-помощник для улучшения отображения данных"""

    @staticmethod
    def format_currency(amount):
        if amount is None:
            return "0.00 ₽"
        return f"{amount:,.2f} ₽".replace(',', ' ')

    @staticmethod
    def get_repair_display_data(repairs, repair_type):
        """Подготовка данных для отображения ремонтов"""
        display_data = []
        for repair in repairs:
            if repair_type == 'active':
                display_data.append({
                    'id': repair.id,
                    'description': SecurityHelper.sanitize_input(repair.description),
                    'start_date': repair.formatted_start_date,
                    'car': repair.request.car.display_info if repair.request else 'Не указан',
                    'cost': repair.cost or 0,
                    'request_date': repair.request.formatted_request_date if repair.request else '',
                    'parts_count': len(repair.spare_parts),
                    'employees': repair.employees,
                    'employees_count': len(repair.employees),
                    'repair_obj': repair
                })
            else:  # completed
                display_data.append({
                    'id': repair.id,
                    'car': repair.car.display_info if repair.car else 'Не указан',
                    'description': SecurityHelper.sanitize_input(
                        repair.repair.description if repair.repair else ''
                    ),
                    'total_cost': repair.total_cost,
                    'completion_date': repair.formatted_completion_date,
                    'work_description': SecurityHelper.sanitize_input(repair.work_description),
                    'parts_count': len(repair.repair.spare_parts) if repair.repair else 0,
                    'employees': repair.repair.employees if repair.repair else [],
                    'employees_count': len(repair.repair.employees) if repair.repair else 0
                })
        return display_data


# ---------- Главная ----------
@bp.route("/")
def index():
    return render_template("index.html")


# ---------- Владельцы ----------
@bp.route("/owners", methods=["GET", "POST"])
def owners():
    if request.method == "POST":
        try:
            # Защита от XSS и инъекций
            last_name = SecurityHelper.sanitize_input(request.form["last_name"])
            first_name = SecurityHelper.sanitize_input(request.form["first_name"])
            middle_name = SecurityHelper.sanitize_input(request.form.get("middle_name", ""))
            phone = SecurityHelper.sanitize_input(request.form["phone"])

            # Валидация телефона
            if not SecurityHelper.validate_phone(phone):
                flash('Неверный формат номера телефона', 'error')
                return redirect(url_for("main.owners"))

            owner = Owner(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                phone=phone,
            )
            db.session.add(owner)
            db.session.commit()
            flash('Владелец успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении владельца', 'error')
        return redirect(url_for("main.owners"))

    owners = Owner.query.all()
    return render_template("owners.html", owners=owners, helper=ViewHelper())


# ---------- Автомобили ----------
@bp.route("/cars", methods=["GET", "POST"])
def cars():
    if request.method == "POST":
        try:
            # Защита от XSS
            number = SecurityHelper.sanitize_input(request.form["number"])
            brand = SecurityHelper.sanitize_input(request.form["brand"])

            car = Car(
                number=number,
                brand=brand,
                release_date=datetime.strptime(request.form["release_date"], "%Y-%m-%d"),
                owner_id=request.form["owner_id"],
            )
            db.session.add(car)
            db.session.commit()
            flash('Автомобиль успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении автомобиля', 'error')
        return redirect(url_for("main.cars"))

    cars = Car.query.all()
    owners = Owner.query.all()
    return render_template("cars.html", cars=cars, owners=owners, helper=ViewHelper())


# ---------- Обращения ----------
@bp.route("/requests", methods=["GET", "POST"])
def requests():
    if request.method == "POST":
        try:
            # Защита от XSS
            issues = SecurityHelper.sanitize_input(request.form["issues"])

            req = ServiceRequest(
                car_id=request.form["car_id"],
                issues=issues,
            )
            db.session.add(req)
            db.session.commit()
            flash('Обращение успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении обращения', 'error')
        return redirect(url_for("main.requests"))

    # Пагинация для обращений
    page = request.args.get('page', 1, type=int)
    per_page = 100

    requests_pagination = ServiceRequest.query.order_by(
        ServiceRequest.request_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    cars = Car.query.all()
    return render_template("requests.html",
                           requests_pagination=requests_pagination,
                           cars=cars,
                           helper=ViewHelper())


# ---------- Ремонты ----------
@bp.route("/repairs", methods=["GET", "POST"])
def repairs():
    if request.method == "POST":
        try:
            # Защита от XSS
            description = SecurityHelper.sanitize_input(request.form["description"])

            repair = Repair(
                request_id=request.form["request_id"],
                description=description,
                cost=float(request.form.get("cost", 0.0)),
            )

            # Добавляем выбранных сотрудников
            employee_ids = request.form.getlist('employee_ids')
            for emp_id in employee_ids:
                employee = Employee.query.get(emp_id)
                if employee:
                    repair.employees.append(employee)

            db.session.add(repair)
            db.session.commit()
            flash('Ремонт успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении ремонта', 'error')
        return redirect(url_for("main.repairs"))

    # Пагинация для активных ремонтов
    page = request.args.get('page', 1, type=int)
    per_page = 100

    # Активные ремонты (без даты завершения) с пагинацией
    active_repairs_pagination = Repair.query.filter(
        Repair.completion_date.is_(None)
    ).order_by(Repair.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # Завершённые ремонты (тоже с пагинацией)
    completed_page = request.args.get('completed_page', 1, type=int)
    completed_repairs_pagination = CompletedWork.query.order_by(
        CompletedWork.completion_date.desc()
    ).paginate(page=completed_page, per_page=per_page, error_out=False)

    # Обращения без активных ремонтов
    active_request_ids = [r.request_id for r in Repair.query.filter(Repair.completion_date.is_(None)).all()]
    requests_ = ServiceRequest.query.filter(~ServiceRequest.id.in_(active_request_ids)).all()

    # Получаем всех сотрудников для начальной загрузки
    employees = Employee.query.order_by(Employee.last_name, Employee.first_name).all()

    # Получаем уникальные значения для фильтров
    positions = db.session.query(Employee.position).distinct().order_by(Employee.position).all()
    positions = [p[0] for p in positions]

    schedules = db.session.query(Employee.schedule).distinct().order_by(Employee.schedule).all()
    schedules = [s[0] for s in schedules]

    active_display = ViewHelper.get_repair_display_data(active_repairs_pagination.items, 'active')
    completed_display = ViewHelper.get_repair_display_data(completed_repairs_pagination.items, 'completed')

    return render_template(
        "repairs.html",
        active_repairs_pagination=active_repairs_pagination,
        completed_repairs_pagination=completed_repairs_pagination,
        active_display=active_display,
        completed_display=completed_display,
        requests=requests_,
        employees=employees,
        positions=positions,
        schedules=schedules,
        helper=ViewHelper()
    )


# ---------- API для фильтрации сотрудников ----------
@bp.route("/api/employees/filter", methods=["GET"])
def api_filter_employees():
    """API для фильтрации сотрудников без перезагрузки страницы"""
    try:
        # Защита от XSS в параметрах запроса
        search_query = SecurityHelper.sanitize_input(request.args.get('search', ''))
        position_filter = SecurityHelper.sanitize_input(request.args.get('position', ''))
        experience_filter = SecurityHelper.sanitize_input(request.args.get('experience', ''))
        schedule_filter = SecurityHelper.sanitize_input(request.args.get('schedule', ''))
        availability_filter = request.args.get('availability', '')

        # Базовый запрос
        employees_query = Employee.query

        # Применяем фильтры с защитой
        if search_query:
            employees_query = employees_query.filter(
                (Employee.last_name.ilike(f'%{search_query}%')) |
                (Employee.first_name.ilike(f'%{search_query}%')) |
                (Employee.middle_name.ilike(f'%{search_query}%'))
            )

        if position_filter:
            employees_query = employees_query.filter(Employee.position == position_filter)

        if experience_filter:
            if experience_filter == 'junior':
                employees_query = employees_query.filter(Employee.experience < 3)
            elif experience_filter == 'middle':
                employees_query = employees_query.filter(Employee.experience.between(3, 8))
            elif experience_filter == 'senior':
                employees_query = employees_query.filter(Employee.experience > 8)

        if schedule_filter:
            employees_query = employees_query.filter(Employee.schedule == schedule_filter)

        # Получаем сотрудников ДО фильтрации занятости
        employees_before_availability = employees_query.all()

        # Фильтр занятости - УПРОЩЕННАЯ РЕАЛИЗАЦИЯ
        if availability_filter:
            filtered_employees = []
            for emp in employees_before_availability:
                active_repairs_count = len([r for r in emp.repairs if not r.is_completed])

                if availability_filter == 'free' and active_repairs_count <= 2:
                    filtered_employees.append(emp)
                elif availability_filter == 'busy' and active_repairs_count > 2:
                    filtered_employees.append(emp)
        else:
            filtered_employees = employees_before_availability

        # Преобразуем в JSON с защитой от XSS
        employees_data = []
        for emp in filtered_employees:
            # Подсчет активных ремонтов для каждого сотрудника
            active_repairs_count = len([r for r in emp.repairs if not r.is_completed])

            employees_data.append({
                'id': emp.id,
                'full_name': SecurityHelper.sanitize_input(emp.full_name),
                'position': SecurityHelper.sanitize_input(emp.position),
                'experience': emp.experience,
                'schedule': SecurityHelper.sanitize_input(emp.schedule),
                'salary': emp.salary,
                'formatted_salary': ViewHelper.format_currency(emp.salary),
                'active_repairs_count': active_repairs_count,
                'availability': 'free' if active_repairs_count <= 2 else 'busy'
            })

        return jsonify({
            'employees': employees_data,
            'count': len(employees_data)
        })

    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Ошибка фильтрации сотрудников: {e}")
        # Защита от утечки информации об ошибках
        return jsonify({
            'error': 'Произошла ошибка при фильтрации сотрудников',
            'employees': [],
            'count': 0
        }), 500


# ---------- Назначение сотрудника на ремонт ----------
@bp.route("/assign_employee/<int:repair_id>", methods=["POST"])
def assign_employee(repair_id):
    try:
        repair = Repair.query.get_or_404(repair_id)
        employee_id = request.form.get('employee_id')

        # Проверка существования сотрудника
        employee = Employee.query.get(employee_id)
        if not employee:
            flash('Сотрудник не найден', 'error')
            return redirect(url_for("main.repairs"))

        if repair.assign_employee(employee_id):
            db.session.commit()
            flash('Сотрудник успешно назначен на ремонт', 'success')
        else:
            flash('Сотрудник уже назначен на этот ремонт', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при назначении сотрудника', 'error')
    return redirect(url_for("main.repairs"))


# ---------- Удаление сотрудника с ремонта ----------
@bp.route("/remove_employee/<int:repair_id>/<int:employee_id>", methods=["POST"])
def remove_employee(repair_id, employee_id):
    try:
        repair = Repair.query.get_or_404(repair_id)

        # Проверка существования сотрудника
        employee = Employee.query.get(employee_id)
        if not employee:
            flash('Сотрудник не найден', 'error')
            return redirect(url_for("main.repairs"))

        if repair.remove_employee(employee_id):
            db.session.commit()
            flash('Сотрудник удален с ремонта', 'success')
        else:
            flash('Сотрудник не был назначен на этот ремонт', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении сотрудника', 'error')
    return redirect(url_for("main.repairs"))


# ---------- Завершение ремонта ----------
@bp.route("/complete/<int:repair_id>")
def complete_repair(repair_id):
    try:
        repair = Repair.query.get_or_404(repair_id)
        repair.completion_date = datetime.utcnow()

        completed = CompletedWork(
            car_id=repair.request.car_id,
            repair_id=repair.id,
            total_cost=repair.total_with_parts,
            completion_date=repair.completion_date,
            work_description=SecurityHelper.sanitize_input(repair.description)
        )

        db.session.add(completed)
        db.session.commit()
        flash('Ремонт успешно завершен', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при завершении ремонта', 'error')
    return redirect(url_for("main.repairs"))


# ---------- Запчасти ----------
@bp.route("/spares", methods=["GET", "POST"])
def spares():
    if request.method == "POST":
        try:
            # Защита от XSS
            name = SecurityHelper.sanitize_input(request.form["name"])
            number = SecurityHelper.sanitize_input(request.form["number"])

            spare = SparePart(
                repair_id=request.form["repair_id"],
                name=name,
                number=number,
                cost=float(request.form.get("cost", 0.0)),
                quantity=int(request.form.get("quantity", 1)),
                installed_date=datetime.utcnow()
            )
            db.session.add(spare)
            db.session.commit()
            flash('Запчасть успешно добавлена', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении запчасти', 'error')
        return redirect(url_for("main.spares"))

    spares = SparePart.query.order_by(SparePart.installed_date.desc()).all()
    repairs = Repair.query.all()
    return render_template("spares.html", spares=spares, repairs=repairs, helper=ViewHelper())


# ---------- Удаление запчасти ----------
@bp.route("/delete_spare/<int:spare_id>", methods=["POST"])
def delete_spare(spare_id):
    try:
        spare = SparePart.query.get_or_404(spare_id)
        db.session.delete(spare)
        db.session.commit()
        flash('Запчасть успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении запчасти', 'error')
    return redirect(url_for("main.spares"))


# ---------- Сотрудники ----------
@bp.route("/employees", methods=["GET", "POST"])
def employees():
    if request.method == "POST":
        try:
            # Защита от XSS и инъекций
            last_name = SecurityHelper.sanitize_input(request.form["last_name"])
            first_name = SecurityHelper.sanitize_input(request.form["first_name"])
            middle_name = SecurityHelper.sanitize_input(request.form.get("middle_name", ""))
            address = SecurityHelper.sanitize_input(request.form["address"])
            phone = SecurityHelper.sanitize_input(request.form["phone"])
            position = SecurityHelper.sanitize_input(request.form["position"])
            schedule = SecurityHelper.sanitize_input(request.form["schedule"])

            # Валидация телефона
            if not SecurityHelper.validate_phone(phone):
                flash('Неверный формат номера телефона', 'error')
                return redirect(url_for("main.employees"))

            emp = Employee(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                birth_date=datetime.strptime(request.form["birth_date"], "%Y-%m-%d"),
                address=address,
                phone=phone,
                position=position,
                salary=float(request.form["salary"]),
                experience=int(request.form["experience"]),
                schedule=schedule,
                bonus=float(request.form.get("bonus", 0.0)),
            )
            db.session.add(emp)
            db.session.commit()
            flash('Сотрудник успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении сотрудника', 'error')
        return redirect(url_for("main.employees"))

    employees = Employee.query.all()
    return render_template("employees.html", employees=employees, helper=ViewHelper())


# ---------- Выполненные работы ----------
@bp.route("/works")
def works():
    works = CompletedWork.query.order_by(CompletedWork.completion_date.desc()).all()
    return render_template("works.html", works=works, helper=ViewHelper())


# ---------- Удаление выполненной работы ----------
@bp.route("/delete_completed_work/<int:work_id>", methods=["POST"])
def delete_completed_work(work_id):
    try:
        work = CompletedWork.query.get_or_404(work_id)
        db.session.delete(work)
        db.session.commit()
        flash('Выполненная работа успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении выполненной работы', 'error')
    return redirect(url_for("main.works"))


# ---------- Очистка старых записей ----------
@bp.route("/cleanup-works", methods=["POST"])
def cleanup_works():
    try:
        deleted_count = CompletedWork.cleanup_old_records(days=365)
        flash(f'Удалено {deleted_count} старых записей', 'success')
    except Exception as e:
        flash('Ошибка при очистке старых записей', 'error')
    return redirect(url_for('main.works'))


# ---------- Получение информации о ремонте для AJAX ----------
@bp.route("/repair_info/<int:repair_id>")
def repair_info(repair_id):
    """API для получения информации о ремонте"""
    try:
        repair = Repair.query.get_or_404(repair_id)
        return jsonify({
            'id': repair.id,
            'description': SecurityHelper.sanitize_input(repair.description),
            'car': repair.request.car.display_info if repair.request else 'Не указан',
            'cost': repair.cost,
            'parts_count': len(repair.spare_parts),
            'employees': [{
                'id': emp.id,
                'name': SecurityHelper.sanitize_input(emp.full_name)
            } for emp in repair.employees]
        })
    except Exception as e:
        return jsonify({'error': 'Ремонт не найден'}), 404