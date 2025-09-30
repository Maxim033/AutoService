import random
from datetime import datetime, timedelta
from autoservice_app import create_app, db
from autoservice_app.models import Owner, Car, Employee, ServiceRequest, Repair, SparePart

app = create_app()

# Данные для генерации
brands = ["Toyota", "BMW", "Audi", "Ford", "Honda", "Nissan", "Mercedes"]
positions = ["Механик", "Менеджер", "Электрик", "Слесарь", "Диагност"]
spare_names = ["Фильтр", "Свеча зажигания", "Тормозной диск", "Фара", "Ремень ГРМ"]

with app.app_context():
    db.drop_all()
    db.create_all()

    # -------- Владельцы --------
    owners = []
    for i in range(1000):  # 🔥 1000 владельцев
        owner = Owner(
            last_name=f"Фамилия{i}",
            first_name=f"Имя{i}",
            middle_name=f"Отчество{i}",
            phone=f"+79{i:09d}"
        )
        owners.append(owner)
        db.session.add(owner)
    db.session.commit()

    # -------- Автомобили --------
    cars = []
    for i in range(1000):  # 🔥 1000 авто
        car = Car(
            number=f"A{i:04d}BC77",
            brand=random.choice(brands),
            release_date=datetime(2000, 1, 1) + timedelta(days=random.randint(0, 8000)),
            owner=random.choice(owners)
        )
        cars.append(car)
        db.session.add(car)
    db.session.commit()

    # -------- Сотрудники --------
    employees = []
    for i in range(1000):  # 🔥 1000 сотрудников
        emp = Employee(
            last_name=f"Работник{i}",
            first_name=f"Имя{i}",
            middle_name=f"Отчество{i}",
            birth_date=datetime(1980, 1, 1) + timedelta(days=random.randint(0, 15000)),
            address=f"Город {i}, ул. Примерная {i}",
            phone=f"+7987{i:07d}",
            position=random.choice(positions),
            salary=random.randint(30000, 90000),
            experience=random.randint(1, 20),
            schedule="5/2",
            bonus=random.randint(0, 10000)
        )
        employees.append(emp)
        db.session.add(emp)
    db.session.commit()

    # -------- Обращения --------
    requests = []
    for i in range(1000):  # 🔥 1000 обращений
        req = ServiceRequest(
            car=random.choice(cars),
            request_date=datetime.utcnow() - timedelta(days=random.randint(0, 1000)),
            issues=f"Неисправность {i}"
        )
        requests.append(req)
        db.session.add(req)
    db.session.commit()

    # -------- Ремонты --------
    repairs = []
    for i in range(1000):  # 🔥 1000 ремонтов
        repair = Repair(
            request=random.choice(requests),
            description=f"Ремонт {i}",
            completion_date=(datetime.utcnow() - timedelta(days=random.randint(0, 500)))
        )
        repairs.append(repair)
        db.session.add(repair)
    db.session.commit()

    # -------- Запчасти --------
    for i in range(1000):  # 🔥 1000 запчастей
        part = SparePart(
            repair=random.choice(repairs),
            name=random.choice(spare_names),
            number=f"DET-{i:05d}"
        )
        db.session.add(part)
    db.session.commit()

    print("✅ База успешно заполнена по 1000 записей в каждой таблице!")
