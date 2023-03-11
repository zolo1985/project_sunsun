from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField, TextAreaField, RadioField
from wtforms.validators import Length, Email, ValidationError, InputRequired, Optional, NumberRange, InputRequired, Regexp
from webapp.database import Connection
from webapp import models
from datetime import datetime, timedelta
import re
import pytz


class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    regions = SelectField('Бүсийн нэр', choices=[], validators=[Optional()])
    status = SelectField('Төлөв', choices=[], validators=[Optional()])
    submit = SubmitField('Шүүх', id="submit1", name="submit1")


class DateFilterForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')


class SelectAccountTypeForm(FlaskForm):
    accounts = SelectField('Дансны төрөл', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')
    

class SelectDriverForm(FlaskForm):
    selected_driver = SelectField('Жолооч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class UnassignForm(FlaskForm):
    order_id = HiddenField()
    submit = SubmitField('Хувиарлагдаагүй төлөвтэй болгох')


class AssignRegionAndDriverForm(FlaskForm):
    order_id = HiddenField()
    select_regions = SelectField('Бүс', choices=[],validators=[Optional()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[Optional()])
    submit = SubmitField('Хувиарлах')


class DriversSelect(FlaskForm):
    task_id = HiddenField()
    select_drivers = SelectField('Жолооч', choices=[], validators=[Optional()])
    submit = SubmitField('Сонгох')


class DriversDateSelect(FlaskForm):
    task_id = HiddenField()
    select_day = SelectField('Өдөр', choices=[], validators=[InputRequired()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class DriversHistoriesForm(FlaskForm):
    task_id = HiddenField()
    date = DateField('Он сараар', validators=[InputRequired()])
    select_drivers = SelectField('Жолооч', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class OrderEditForm(FlaskForm):
    status = SelectField('Төлөв', choices=[],validators=[Optional()])
    driver_comment = TextAreaField('Жолоочийн коммент', validators=[Optional()])
    comment = TextAreaField('Дотоод коммент', validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[Optional()])
    khoroo = SelectField('Хорооны дугаар', choices=[],validators=[Optional()])
    district = SelectField('Дүүрэг', choices=[],validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[],validators=[Optional()])
    phone = StringField('Утасны дугаар',validators=[ Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    instruction = TextAreaField('Жолоочид заавар', validators=[Optional()])
    total_amount = IntegerField('Хүргэлтийн дүн', validators=[Optional(), NumberRange(min=0)])
    select_regions = SelectField('Бүс өөрчлөх', choices=[],validators=[Optional()])
    select_drivers = SelectField('Жолооч өөрчлөх', choices=[], validators=[Optional()])
    delivery_date = DateField('Он сар өөрчлөх', validators=[Optional()])
    postphoned_date = DateField('Хойшлуулах огноо', validators=[Optional()])
    submit = SubmitField('Төлөв өөрчлөх')

    def validate_date(self, postphoned_date):
        tomorrow = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date() + timedelta(days=1)
        if postphoned_date.data < tomorrow:
            raise ValidationError("Өнөөдрөөс өмнөх өдөр байх боломжгүй!")


class FilterOrderByDistrict(FlaskForm):
    khoroo_names = SelectField('Хорооны дугаар', choices=[],validators=[Optional()])
    district_names = SelectField('Дүүрэгийн нэр', choices=[],validators=[InputRequired()])
    submit = SubmitField('Шүүж харах')


class FilterDateForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')


class ShowCommentStatusForm(FlaskForm):
    order_id = HiddenField()
    submit = SubmitField('Бүх Төлөв, Коммент Нээх')


class EditCommentForm(FlaskForm):
    comment = TextAreaField('Коммент', validators=[Optional()])
    submit = SubmitField('Коммент Өөрчлөх')


class EditAddressForm(FlaskForm):
    address = TextAreaField('Хаяг', validators=[Optional()])
    submit = SubmitField('Хаяг Өөрчлөх')


class EditTotalAmountForm(FlaskForm):
    total_amount = IntegerField('Дүн', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Дүн Өөрчлөх')


class EditOrderStateForm(FlaskForm):
    select_state = SelectField('Өөрчлөх төлөв сонгох', choices=[], validators=[InputRequired()])
    comment = TextAreaField('Тайлбар', validators=[Optional()])
    submit = SubmitField('Өөрчлөх')


class NewAccountForm(FlaskForm):
    company_name = StringField('Байгууллагын нэр', validators=[InputRequired(), Length(min=2, max=255, message='Хэт урт эсвэл богино байна!')])
    firstname = StringField('Нэр', validators=[InputRequired()])
    lastname = StringField('Овог', validators=[InputRequired()])
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар',validators=[ InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    password = PasswordField('Нууц үг', validators=[InputRequired(), Length(min=3, max=50)])
    select_user_role = SelectField('Хэрэглэгчийн төрөл', choices=[], validators=[InputRequired()])
    submit = SubmitField('Хэрэглэгч нэмэх')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ- "))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ- "))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_email(self, email):
        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data).first()
        if len(account)>1:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).first()
        if len(account)>1:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


class EditAccountForm(FlaskForm):
    lastname = StringField('Овог', validators=[InputRequired()])
    firstname = StringField('Нэр', validators=[InputRequired()])
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар',validators=[InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    delivery_rate = IntegerField('Жолоочийн төлбөр', validators=[Optional(), NumberRange(min=0)])
    supplier_rate = IntegerField('Хүргэлтийн төлбөр', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

    def validate_email(self, email):
        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data).all()
        if len(account)>1:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).all()
        if len(account)>1:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


class SelectOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[InputRequired()])
    date = DateField('Он сар', validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SelectDriverOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[InputRequired()])
    select_driver = SelectField('Жолооч', choices=[],validators=[InputRequired()])
    date = DateField('Он сар', validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SelectSupplierOption(FlaskForm):
    select_option = SelectField('Хугацаа', choices=[],validators=[InputRequired()])
    select_supplier = SelectField('Харилцагч', choices=[],validators=[InputRequired()])
    date = DateField('Он сар', validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class SearchForm(FlaskForm):
    search_mode = RadioField(choices=[(0,'Текст'),(1,'ID')], validators=[Optional()], default=0)
    search_text = StringField('Хайх', validators=[Optional(), Length(min=1, max=50, message='Нэр 1-50 урттай')])
    search_types = SelectField('Төрөл', choices=['Хүргэлт', 'Агуулах'], validators=[InputRequired()])
    submit = SubmitField('Хайх')


class SelectSupplierForm(FlaskForm):
    suppliers = SelectField('Харилцагч', choices=[], validators=[InputRequired()])


class OrderAddForm(FlaskForm):
    delivery_type = RadioField('Төрөл', choices=[(0,'Хүргэлт'),(1,'Агуулахаас')], validators=[Optional()], default=0)
    order_type = RadioField('Хүргэлтийн чиглэл', choices=[(0,'Улаанбаатар'),(1,'Орон нутаг')], validators=[Optional()], default=0)
    suppliers = SelectField('Харилцагч', choices=[], validators=[InputRequired()])
    phone = StringField('Утасны дугаар',validators=[ InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    phone_more = StringField('Нэмэлт утасны дугаар*. (Заавал биш)',validators=[Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    district = SelectField('Дүүрэг', choices=[], validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[], validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    total_amount = IntegerField('Нийт үнэ', validators=[InputRequired(), NumberRange(min=0)], default=0)
    submit = SubmitField('Үүсгэх')


class OrderDetailEditForm(FlaskForm):
    submit = SubmitField('Өөрчлөх')


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