# populate_1000.py
from autoservice_app import create_app, db
from autoservice_app.models import Owner, Car, Employee, ServiceRequest, Repair, SparePart, CompletedWork, \
    repair_employees
from datetime import datetime, timedelta
import random
import string
from sqlalchemy import text  # Добавляем импорт text

app = create_app()

# Глобальные множества для отслеживания уникальных значений
used_phones = set()
used_car_numbers = set()
used_employee_phones = set()


def generate_unique_phone():
    """Генерация уникального номера телефона"""
    while True:
        phone = f"+79{random.randint(100000000, 999999999)}"
        if phone not in used_phones:
            used_phones.add(phone)
            return phone


def generate_unique_car_number():
    """Генерация уникального номера автомобиля"""
    while True:
        first_letter = random.choice(string.ascii_uppercase)
        second_letter = random.choice(string.ascii_uppercase)
        numbers = ''.join(random.choices(string.digits, k=3))
        car_number = f"{first_letter}{second_letter}{numbers}177"

        if car_number not in used_car_numbers:
            used_car_numbers.add(car_number)
            return car_number


def generate_unique_employee_phone():
    """Генерация уникального номера телефона для сотрудника"""
    while True:
        phone = f"+79{random.randint(100000000, 999999999)}"
        if phone not in used_employee_phones and phone not in used_phones:
            used_employee_phones.add(phone)
            return phone


def generate_name(prefix, i):
    """Генерация имени с русскими фамилиями"""
    last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Попов", "Васильев", "Соколов", "Михайлов",
                  "Новиков",
                  "Федоров", "Морозов", "Волков", "Алексеев", "Лебедев", "Семенов", "Егоров", "Павлов", "Козлов",
                  "Степанов"]
    first_names = ["Александр", "Дмитрий", "Максим", "Сергей", "Андрей", "Алексей", "Артем", "Илья", "Кирилл", "Михаил",
                   "Никита", "Матвей", "Роман", "Егор", "Георгий", "Владимир", "Павел", "Константин", "Тимофей",
                   "Вячеслав"]
    middle_names = ["Александрович", "Дмитриевич", "Сергеевич", "Андреевич", "Алексеевич", "Игоревич", "Олегович",
                    "Владимирович",
                    "Николаевич", "Викторович", "Юрьевич", "Борисович", "Геннадьевич", "Евгеньевич", "Валентинович"]

    return {
        'last_name': f"{random.choice(last_names)}{i}",
        'first_name': f"{random.choice(first_names)}{i}",
        'middle_name': f"{random.choice(middle_names)}{i}"
    }


def populate_1000_records():
    with app.app_context():
        print("🔄 Начинаем заполнение базы данных 1000 записями в каждой таблице...")

        # Очищаем существующие данные
        print("🧹 Очищаем старые данные...")
        try:
            # Очищаем связующую таблицу многие-ко-многим
            db.session.execute(repair_employees.delete())
            db.session.query(CompletedWork).delete()
            db.session.query(SparePart).delete()
            db.session.query(Repair).delete()
            db.session.query(ServiceRequest).delete()
            db.session.query(Car).delete()
            db.session.query(Owner).delete()
            db.session.query(Employee).delete()
            db.session.commit()
            print("✅ Старые данные удалены")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Ошибка при удалении старых данных: {e}")
            print("Продолжаем заполнение...")

        # Данные для генерации
        brands = ["Toyota", "BMW", "Audi", "Ford", "Honda", "Nissan", "Mercedes", "Volkswagen", "Hyundai", "Kia",
                  "Lada", "Chevrolet", "Renault", "Mazda", "Subaru", "Lexus", "Infiniti", "Volvo", "Skoda", "Peugeot"]
        positions = ["Механик", "Менеджер", "Электрик", "Слесарь", "Диагност", "Мастер", "Консультант", "Администратор",
                     "Старший механик", "Технический специалист", "Приемщик", "Мойщик", "Шиномонтажник"]
        spare_names = ["Фильтр масляный", "Свеча зажигания", "Тормозной диск", "Фара", "Ремень ГРМ",
                       "Аккумулятор", "Шина", "Тормозная колодка", "Амортизатор", "Стартер", "Генератор",
                       "Топливный насос", "Радиатор", "Сцепление", "Карбюратор", "Инжектор", "Турбина"]
        issues_list = ["Замена масла", "Ремонт тормозной системы", "Диагностика двигателя", "Замена фильтров",
                       "Ремонт подвески", "Замена аккумулятора", "Балансировка колес", "Ремонт выхлопной системы",
                       "Замена ремня ГРМ", "Чип-тюнинг", "Ремонт КПП", "Замена сцепления", "Кузовной ремонт",
                       "Покраска", "Замена стекол", "Ремонт электроники", "Обслуживание кондиционера"]

        # -------- Владельцы (1000) --------
        print("👥 Создаем 1000 владельцев...")
        owners = []
        for i in range(1000):
            name_data = generate_name("Owner", i)
            owner = Owner(
                last_name=name_data['last_name'],
                first_name=name_data['first_name'],
                middle_name=name_data['middle_name'],
                phone=generate_unique_phone()
            )
            owners.append(owner)
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(owners)
                owners = []
                print(f"   Создано {i} владельцев")

        if owners:
            db.session.bulk_save_objects(owners)
        db.session.commit()
        print("✅ 1000 владельцев создано")

        # -------- Автомобили (1000) --------
        print("🚗 Создаем 1000 автомобилей...")
        cars = []
        for i in range(1000):
            try:
                car = Car(
                    number=generate_unique_car_number(),
                    brand=random.choice(brands),
                    release_date=datetime(2000, 1, 1) + timedelta(days=random.randint(0, 8000)),
                    owner_id=random.randint(1, 1000)
                )
                cars.append(car)
            except Exception as e:
                print(f"Ошибка при создании автомобиля {i}: {e}")
                continue

            if i % 100 == 0 and i > 0:
                try:
                    db.session.bulk_save_objects(cars)
                    cars = []
                    print(f"   Создано {i} автомобилей")
                except Exception as e:
                    print(f"Ошибка при сохранении автомобилей: {e}")
                    db.session.rollback()

        if cars:
            try:
                db.session.bulk_save_objects(cars)
            except Exception as e:
                print(f"Ошибка при финальном сохранении автомобилей: {e}")
                # Попробуем сохранить по одному
                for car in cars:
                    try:
                        db.session.add(car)
                        db.session.commit()
                    except:
                        db.session.rollback()
                        continue

        db.session.commit()
        print("✅ 1000 автомобилей создано")

        # -------- Сотрудники (1000) --------
        print("👨‍💼 Создаем 1000 сотрудников...")
        employees = []
        for i in range(1000):
            name_data = generate_name("Employee", i)
            emp = Employee(
                last_name=name_data['last_name'],
                first_name=name_data['first_name'],
                middle_name=name_data['middle_name'],
                birth_date=datetime(1970, 1, 1) + timedelta(days=random.randint(0, 15000)),
                address=f"г. Москва, ул. {random.choice(['Ленина', 'Пушкина', 'Гагарина', 'Советская', 'Мира'])}, д. {random.randint(1, 200)}",
                phone=generate_unique_employee_phone(),
                position=random.choice(positions),
                salary=random.randint(30000, 120000),
                experience=random.randint(1, 30),
                schedule=random.choice(["5/2", "2/2", "сменный", "гибкий"]),
                bonus=random.randint(0, 20000)
            )
            employees.append(emp)
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(employees)
                employees = []
                print(f"   Создано {i} сотрудников")

        if employees:
            db.session.bulk_save_objects(employees)
        db.session.commit()
        print("✅ 1000 сотрудников создано")

        # -------- Обращения (1000) --------
        print("📋 Создаем 1000 обращений...")
        requests = []
        for i in range(1000):
            req = ServiceRequest(
                car_id=random.randint(1, 1000),
                request_date=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                issues=f"{random.choice(issues_list)} - {random.choice(['срочно', 'планово', 'по гарантии', 'внепланово'])}"
            )
            requests.append(req)
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(requests)
                requests = []
                print(f"   Создано {i} обращений")

        if requests:
            db.session.bulk_save_objects(requests)
        db.session.commit()
        print("✅ 1000 обращений создано")

        # -------- Ремонты (1000) --------
        print("🔧 Создаем 1000 ремонтов...")
        repairs = []
        for i in range(1000):
            is_completed = random.choice([True, False, False, True])  # 50% шанс завершения
            completion_date = datetime.utcnow() - timedelta(days=random.randint(1, 180)) if is_completed else None

            repair = Repair(
                request_id=random.randint(1, 1000),
                description=f"Ремонт {i + 1}: {random.choice(issues_list)} - {random.choice(['качественно', 'быстро', 'с гарантией', 'профессионально'])}",
                completion_date=completion_date,
                cost=random.randint(1000, 50000)
            )
            repairs.append(repair)
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(repairs)
                repairs = []
                print(f"   Создано {i} ремонтов")

        if repairs:
            db.session.bulk_save_objects(repairs)
        db.session.commit()
        print("✅ 1000 ремонтов создано")

        # -------- Назначение сотрудников на ремонты --------
        print("👥 Назначаем сотрудников на ремонты...")
        all_repairs = Repair.query.all()
        all_employees = Employee.query.all()

        assignments_count = 0
        for repair in all_repairs:
            # Назначаем от 1 до 3 случайных сотрудников на каждый ремонт
            num_employees = random.randint(1, 3)
            assigned_employees = random.sample(all_employees, min(num_employees, len(all_employees)))

            for employee in assigned_employees:
                repair.employees.append(employee)
                assignments_count += 1

            if assignments_count % 500 == 0 and assignments_count > 0:
                db.session.commit()
                print(f"   Назначено {assignments_count} связей сотрудник-ремонт")

        db.session.commit()
        print(f"✅ Назначено {assignments_count} связей сотрудник-ремонт")

        # -------- Запчасти (1000) --------
        print("🔩 Создаем 1000 запчастей...")
        spares = []
        for i in range(1000):
            spare = SparePart(
                repair_id=random.randint(1, 1000),
                name=f"{random.choice(spare_names)} {random.choice(['премиум', 'стандарт', 'оригинал', 'аналог'])}",
                number=f"SP-{random.randint(10000, 99999)}-{i}",
                cost=random.randint(500, 15000),
                quantity=random.randint(1, 5),
                installed_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            spares.append(spare)
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(spares)
                spares = []
                print(f"   Создано {i} запчастей")

        if spares:
            db.session.bulk_save_objects(spares)
        db.session.commit()
        print("✅ 1000 запчастей создано")

        # -------- Выполненные работы (1000) --------
        print("✅ Создаем выполненные работы...")
        completed_works = []
        # Берем только завершенные ремонты
        completed_repairs = Repair.query.filter(Repair.completion_date.isnot(None)).all()

        print(f"   Найдено {len(completed_repairs)} завершенных ремонтов для создания работ")

        for i, repair in enumerate(completed_repairs):
            work = CompletedWork(
                car_id=repair.request.car_id,
                repair_id=repair.id,
                total_cost=repair.cost + random.randint(0, 5000),
                completion_date=repair.completion_date,
                work_description=f"Выполнено: {repair.description}"
            )
            completed_works.append(work)
            if i % 100 == 0 and i > 0:
                db.session.bulk_save_objects(completed_works)
                completed_works = []
                print(f"   Создано {i} выполненных работ")

        if completed_works:
            db.session.bulk_save_objects(completed_works)
        db.session.commit()
        print(f"✅ Создано {len(completed_repairs)} выполненных работ")

        # -------- Финальная статистика --------
        print("\n🎉 База данных успешно заполнена!")
        print("📊 Финальная статистика:")
        print(f"   👥 Владельцы: {Owner.query.count()} записей")
        print(f"   🚗 Автомобили: {Car.query.count()} записей")
        print(f"   👨‍💼 Сотрудники: {Employee.query.count()} записей")
        print(f"   📋 Обращения: {ServiceRequest.query.count()} записей")
        print(f"   🔧 Ремонты: {Repair.query.count()} записей")
        print(f"   🔩 Запчасти: {SparePart.query.count()} записей")
        print(f"   ✅ Выполненные работы: {CompletedWork.query.count()} записей")

        # Дополнительная статистика по ремонтам
        active_repairs_count = Repair.query.filter(Repair.completion_date.is_(None)).count()
        completed_repairs_count = Repair.query.filter(Repair.completion_date.isnot(None)).count()
        print(f"\n🔧 Статистика ремонтов:")
        print(f"   Активные ремонты: {active_repairs_count}")
        print(f"   Завершенные ремонты: {completed_repairs_count}")

        # Статистика по связям сотрудник-ремонт (исправленная версия)
        try:
            repair_employee_count = db.session.execute(
                text("SELECT COUNT(*) FROM repair_employees")  # Используем text() для SQL выражений
            ).scalar()
            print(f"   Связей сотрудник-ремонт: {repair_employee_count}")
        except Exception as e:
            print(f"   Ошибка при подсчете связей сотрудник-ремонт: {e}")
            # Альтернативный способ подсчета
            total_assignments = 0
            for repair in Repair.query.all():
                total_assignments += len(repair.employees)
            print(f"   Связей сотрудник-ремонт (альтернативный подсчет): {total_assignments}")

        # Статистика по сотрудникам
        print(f"\n👨‍💼 Статистика по сотрудникам:")
        top_positions = positions[:5]  # Покажем для первых 5 должностей
        for position in top_positions:
            count = Employee.query.filter_by(position=position).count()
            if count > 0:
                avg_salary = db.session.query(db.func.avg(Employee.salary)).filter_by(position=position).scalar()
                print(f"   {position}: {count} чел., средняя з/п: {avg_salary:,.0f} ₽")

        # Статистика по распределению сотрудников по ремонтам
        print(f"\n📈 Распределение сотрудников по ремонтам:")
        repairs_with_employees = Repair.query.filter(Repair.employees.any()).count()
        print(f"   Ремонтов с назначенными сотрудниками: {repairs_with_employees}")
        print(f"   Ремонтов без сотрудников: {Repair.query.count() - repairs_with_employees}")

        # Среднее количество сотрудников на ремонт
        if repairs_with_employees > 0:
            avg_employees_per_repair = assignments_count / repairs_with_employees
            print(f"   Среднее сотрудников на ремонт: {avg_employees_per_repair:.1f}")

        print("\n✨ Заполнение базы данных завершено успешно!")


if __name__ == "__main__":
    populate_1000_records()