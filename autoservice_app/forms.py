from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length

# ------- Владельцы -------
class OwnerForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(max=64)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(max=64)])
    middle_name = StringField('Отчество', validators=[Length(max=64)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Сохранить')

# ------- Авто -------
class CarForm(FlaskForm):
    number = StringField('Номер', validators=[DataRequired(), Length(max=20)])
    brand = StringField('Марка', validators=[DataRequired(), Length(max=64)])
    release_date = DateField('Дата выпуска', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# ------- Обращения -------
class ServiceRequestForm(FlaskForm):
    request_date = DateField('Дата обращения', validators=[DataRequired()])
    issues = TextAreaField('Неисправности', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# ------- Ремонт -------
class RepairForm(FlaskForm):
    description = TextAreaField('Описание ремонта', validators=[DataRequired()])
    completion_date = DateField('Дата завершения')
    submit = SubmitField('Сохранить')

# ------- Запчасть -------
class SparePartForm(FlaskForm):
    name = StringField('Название детали', validators=[DataRequired()])
    number = StringField('Номер детали', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

# ------- Сотрудник -------
class EmployeeForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    birth_date = DateField('Дата рождения', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    salary = FloatField('Оклад', validators=[DataRequired()])
    experience = IntegerField('Стаж (лет)', validators=[DataRequired()])
    schedule = StringField('Режим работы', validators=[DataRequired()])
    bonus = FloatField('Надбавка за стаж')
    submit = SubmitField('Сохранить')
