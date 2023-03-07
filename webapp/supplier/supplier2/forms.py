from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField, RadioField, PasswordField
from wtforms.validators import ValidationError, Optional, NumberRange, InputRequired, Length, Regexp
import re

class OrderAddForm(FlaskForm):
    order_type = RadioField('Хүргэлтийн чиглэл', choices=[(0,'Улаанбаатар'),(1,'Орон нутаг')], validators=[Optional()], default=0)
    phone = StringField('Утасны дугаар',validators=[ Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    phone_more = StringField('Нэмэлт утасны дугаар*. (Заавал биш)',validators=[Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    district = SelectField('Дүүрэг', choices=[], validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[], validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[Optional()])
    comment = TextAreaField('Нэмэлт мэдээлэл*. (Заавал биш)', validators=[Optional()])
    total_amount = IntegerField('Нийт үнэ', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Үүсгэх')


class OrderEditForm(FlaskForm):
    phone = StringField('Утасны дугаар',validators=[ InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    phone_more = StringField('Нэмэлт утасны дугаар*. (Заавал биш)',validators=[Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    district = SelectField('Дүүрэг', choices=[],validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[],validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    total_amount = IntegerField('Үйлчлэгчээс авах дүн', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')


class DateSelectForm(FlaskForm):
    date = DateField('Он Сар', validators=[Optional()])
    submit = SubmitField('Сонгох')
    

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

    def validate_password_again(self, confirm_password, password):
        if password.data != confirm_password.data:
            raise ValidationError('Нууц үгнүүд таарахгүй байна!')


class DateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')
    

class SearchForm(FlaskForm):
    search_text = StringField('Хайх', validators=[InputRequired(), Length(min=1, max=50, message='Нэр 1-50 урттай')])
    submit = SubmitField('Хайх')