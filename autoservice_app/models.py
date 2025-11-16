from datetime import datetime
from . import db


# Таблица для связи многие-ко-многим между ремонтами и сотрудниками
repair_employees = db.Table('repair_employees',
    db.Column('repair_id', db.Integer, db.ForeignKey('repair.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), primary_key=True),
    db.Column('assigned_date', db.Date, default=datetime.utcnow)
)


class Owner(db.Model):
    __tablename__ = 'owner'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    phone = db.Column(db.String(20), unique=True, nullable=False)
    cars = db.relationship('Car', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Owner {self.last_name} {self.first_name}>'

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()


class Car(db.Model):
    __tablename__ = 'car'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    brand = db.Column(db.String(64), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    requests = db.relationship('ServiceRequest', backref='car', lazy=True, cascade='all, delete-orphan')
    completed_works = db.relationship('CompletedWork', backref='car', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Car {self.brand} {self.number}>'

    @property
    def display_info(self):
        return f"{self.brand} ({self.number})"


class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    request_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    issues = db.Column(db.Text, nullable=False)
    repairs = db.relationship('Repair', backref='request', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ServiceRequest {self.id} for Car {self.car_id}>'

    @property
    def formatted_request_date(self):
        return self.request_date.strftime("%d.%m.%Y") if self.request_date else ""


class Repair(db.Model):
    __tablename__ = 'repair'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completion_date = db.Column(db.Date)
    cost = db.Column(db.Float, default=0.0)
    spare_parts = db.relationship('SparePart', backref='repair', lazy=True, cascade='all, delete-orphan')
    completed_works = db.relationship('CompletedWork', backref='repair', lazy=True, cascade='all, delete-orphan')
    # Связь многие-ко-многим с сотрудниками
    employees = db.relationship('Employee', secondary=repair_employees,
                               backref=db.backref('repairs', lazy=True))

    def __repr__(self):
        return f'<Repair {self.id}>'

    @property
    def is_completed(self):
        return self.completion_date is not None

    @property
    def start_date(self):
        return self.request.request_date if self.request else None

    @property
    def formatted_start_date(self):
        return self.start_date.strftime("%d.%m.%Y") if self.start_date else "Не указана"

    @property
    def formatted_completion_date(self):
        return self.completion_date.strftime("%d.%m.%Y") if self.completion_date else "В процессе"

    @property
    def total_with_parts(self):
        """Общая стоимость ремонта с учетом запчастей"""
        parts_cost = sum(part.total_cost for part in self.spare_parts)
        return self.cost + parts_cost

    @property
    def assigned_employees_names(self):
        """Список имен назначенных сотрудников"""
        return [emp.full_name for emp in self.employees]

    def assign_employee(self, employee_id):
        """Назначить сотрудника на ремонт"""
        employee = Employee.query.get(employee_id)
        if employee and employee not in self.employees:
            self.employees.append(employee)
            return True
        return False

    def remove_employee(self, employee_id):
        """Убрать сотрудника с ремонта"""
        employee = Employee.query.get(employee_id)
        if employee and employee in self.employees:
            self.employees.remove(employee)
            return True
        return False


class SparePart(db.Model):
    __tablename__ = 'spare_part'

    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repair.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    number = db.Column(db.String(64), nullable=False)
    cost = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Integer, default=1)
    installed_date = db.Column(db.Date, default=datetime.utcnow)

    def __repr__(self):
        return f'<SparePart {self.name} {self.number}>'

    @property
    def total_cost(self):
        return self.cost * self.quantity

    @property
    def formatted_installed_date(self):
        return self.installed_date.strftime("%d.%m.%Y") if self.installed_date else ""


class Employee(db.Model):
    __tablename__ = 'employee'

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

    def __repr__(self):
        return f'<Employee {self.last_name} {self.first_name}>'

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    @property
    def total_salary(self):
        return self.salary + (self.bonus or 0)

    @property
    def current_repairs_count(self):
        """Количество активных ремонтов сотрудника"""
        return len([r for r in self.repairs if not r.is_completed])

    @property
    def completed_repairs_count(self):
        """Количество завершенных ремонтов сотрудника"""
        return len([r for r in self.repairs if r.is_completed])


class CompletedWork(db.Model):
    __tablename__ = 'completed_work'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    repair_id = db.Column(db.Integer, db.ForeignKey('repair.id'), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    completion_date = db.Column(db.Date, default=datetime.utcnow)
    work_description = db.Column(db.Text)

    def __repr__(self):
        return f'<CompletedWork {self.id} for Car {self.car_id}>'

    @property
    def formatted_completion_date(self):
        return self.completion_date.strftime("%d.%m.%Y") if self.completion_date else "Не указана"

    @classmethod
    def cleanup_old_records(cls, days=365):
        from datetime import timedelta
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        old_records = cls.query.filter(cls.completion_date < cutoff_date).all()

        for record in old_records:
            db.session.delete(record)

        db.session.commit()
        return len(old_records)