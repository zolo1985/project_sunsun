from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, DateTimeField, IntegerField, TextAreaField
from wtforms.validators import Length, ValidationError, InputRequired, Optional, NumberRange, InputRequired
import re

class FiltersForm(FlaskForm):
    order_id = HiddenField()
    drivers = SelectField('Жолоочийн нэр', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')

class ReceivePaymentForm(FlaskForm):
    order_id = HiddenField()
    net_amount = HiddenField()
    total_amount = IntegerField('Нийт', validators=[Optional(), NumberRange(min=0)])
    remaining_amount = IntegerField('Үлдэгдэл', validators=[Optional(), NumberRange(min=0)])
    comment = TextAreaField('Тэмдэглэгээ', validators=[Optional()])
    submit = SubmitField('Тооцоо хийх', id="submitButton")

class PaymentReceived(FlaskForm):
    submit = SubmitField('Тооцоогүй болгох')

class DateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')

class DateTimeSelect(FlaskForm):
    select_date = DateTimeField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')

class SupplierDateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[InputRequired()])
    submit = SubmitField('Сонгох')

class SearchForm(FlaskForm):
    search_text = StringField('Хайх', validators=[InputRequired(), Length(min=1, max=50, message='Нэр 1-50 урттай')])
    search_types = SelectField('Төрөл', choices=['Хүргэлт', 'Агуулах'], validators=[InputRequired()])
    submit = SubmitField('Хайх')

class PasswordChangeForm(FlaskForm):
    user_id = HiddenField()
    current_password = PasswordField('Одоо хэрэглэж байгаа нууц үг', validators=[InputRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    password = PasswordField('Шинэ нууц үг', validators=[InputRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    confirm_password = PasswordField('Дахин шинэ нууц үг', validators=[InputRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    submit = SubmitField('Нууц үг өөрчлөх')

    def validate_password(self, password):
        flag = 0
        while True:  
            if (len(password.data)<8):
                flag = -1
                raise ValidationError('Нууц үг хамгийн багадаа 8 тэмдэгтэй!')
            elif not re.search("[a-z]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 жижиг үсэг оролцуулсан байх ёстой!')
            elif not re.search("[A-Z]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 том үсэг оролцуулсан байх ёстой!')
            elif not re.search("[0-9]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа 1 тоо оролцуулсан байх ёстой!')
            elif not re.search("[_@$!]", password.data):
                flag = -1
                raise ValidationError('Нууц үг заавал багадаа _, @, $, ! аль нэгийг тусгай тэмдэгтийг оролцуулсан байх ёстой!')
            else:
                flag = 0
                break
        
        if flag ==-1:
            pass

        if password.data != password.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_password_again(self, confirm_password, password):
        if password.data != confirm_password.data:
            raise ValidationError('Нууц үгнүүд таарахгүй байна!')