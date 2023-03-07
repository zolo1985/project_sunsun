from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, HiddenField, SelectField, DateField, TextAreaField, IntegerField
from wtforms.validators import Length, ValidationError, InputRequired, Optional, InputRequired, NumberRange
import re
from datetime import datetime, timedelta
import pytz

class DateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')

class DeliveryStatusForm(FlaskForm):
    current_status = SelectField('Төлөв өөрчлөх', choices=[], validators=[Optional()])
    submit = SubmitField('Төлөв өөрчлөх')

class DeliveryCompletedForm(FlaskForm):
    driver_comment = TextAreaField('Нэмэлт тэмдэглэгээ', validators=[Optional()])
    received_amount = IntegerField('Авсан дүн', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Захиалга хүргэх')

class DeliveryPostphonedForm(FlaskForm):
    driver_comment = TextAreaField('Шалтгаан', validators=[Optional()])
    postphoned_date = DateField('Хойшлуулсан өдөр', validators=[InputRequired()])
    submit = SubmitField('Захиалга хойшлуулах')

    def validate_date(self, postphoned_date):
        tomorrow = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date() + timedelta(days=1)
        if postphoned_date.data < tomorrow:
            raise ValidationError("Өнөөдрөөс өмнөх өдөр байх боломжгүй!")

class DeliveryCancelledForm(FlaskForm):
    driver_comment = TextAreaField('Шалтгаан', validators=[Optional()])
    submit = SubmitField('Захиалга цуцлах')

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