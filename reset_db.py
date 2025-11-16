import os
import sqlite3
from autoservice_app import create_app, db
from autoservice_app.models import Owner, Car, Employee, ServiceRequest, Repair, SparePart, CompletedWork


def reset_database():
    print("🔄 Пересоздание базы данных...")

    app = create_app()

    with app.app_context():
        # Удаляем старую базу если существует
        db_path = 'autoservice.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️ Удалена старая база данных")

        # Создаем все таблицы
        db.create_all()
        print("✅ Все таблицы созданы!")

        # Проверяем созданные таблицы
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        print("📊 Созданные таблицы:")
        for table in tables:
            print(f"   - {table[0]}")

        # Добавляем тестовые данные
        add_test_data()
        print("🎉 База данных готова к использованию!")


def add_test_data():
    """Добавляем тестовые данные для проверки"""
    try:
        # Добавляем тестового сотрудника
        employee = Employee(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
            birth_date="1990-01-01",
            address="Москва, ул. Тестовая, 1",
            phone="+79123456789",
            position="Механик",
            salary=50000.0,
            experience=5,
            schedule="5/2",
            bonus=5000.0
        )
        db.session.add(employee)

        # Добавляем тестового владельца
        owner = Owner(
            last_name="Петров",
            first_name="Петр",
            middle_name="Петрович",
            phone="+79123456780"
        )
        db.session.add(owner)

        db.session.commit()
        print("✅ Тестовые данные добавлены")

    except Exception as e:
        print(f"⚠️ Ошибка при добавлении тестовых данных: {e}")
        db.session.rollback()


if __name__ == "__main__":
    reset_database()