from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField
from wtforms.validators import Length, Email, ValidationError, InputRequired, Optional, NumberRange, InputRequired
from webapp.database import Connection
from flask_wtf.file import FileField, FileAllowed
from webapp import models
import re


class SelectAccountTypeForm(FlaskForm):
    accounts = SelectField('Дансны төрөл', choices=[], validators=[InputRequired()])
    submit = SubmitField('Сонгох')


class NewAccountForm(FlaskForm):
    company_name = StringField('Байгууллагын нэр', validators=[Optional(), Length(min=6, max=255, message='Хэт урт эсвэл богино байна!')])
    firstname = StringField('Нэр', validators=[InputRequired()])
    lastname = StringField('Овог', validators=[InputRequired()])
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар', validators=[InputRequired()])
    password = PasswordField('Нууц үг', validators=[InputRequired(), Length(min=3, max=50)])
    select_user_role = SelectField('Хэрэглэгчийн төрөл', choices=[], validators=[InputRequired()])
    submit = SubmitField('Хэрэглэгч нэмэх')

    def validate_company_name(self, company_name):
        connection = Connection()
        is_company_name = connection.query(models.User).filter_by(company_name=company_name.data).count()
        connection.close()
        if is_company_name>=1:
            raise ValidationError('Ийм нэртэй харилцагч бүртгэлтэй байна! Өөр нэр сонгоно уу!')

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
        connection.close()
        if account:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789+"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).first()
        connection.close()
        if account:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


class EditAccountForm(FlaskForm):
    email = StringField('И-мэйл', validators=[InputRequired(), Email(message='И-мэйл хаяг оруулна уу!')])
    phone = StringField('Утасны дугаар', validators=[InputRequired()])
    supplier_rate = IntegerField('Хүргэлтийн төлбөр', validators=[InputRequired(), NumberRange(min=0)])
    submit = SubmitField('Өөрчлөх')

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

        if firstname.data != firstname.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг ашиглана уу!')

        if lastname.data != lastname.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_email(self, email):
        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data).all()
        connection.close()
        if len(account)>1:
            raise ValidationError('Энэ имэйл хаяг өөр данс нь дээр бүртгэлтэй байна! Өөр имэйл хаяг ашиглана уу!')

    def validate_phone(self, phone):
        allowed_chars = set(("0123456789+"))
        validation = set((phone.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн тоо ашиглана уу!')

        if phone.data != phone.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).all()
        connection.close()
        if len(account)>1:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')


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
            elif re.search("\s", password.data):
                flag = -1
                raise ValidationError('Урд хойно хоосон зай ашигласан байна! Арилгана уу!')
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


class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    regions = SelectField('Бүсийн нэр', choices=[], validators=[Optional()])
    status = SelectField('Төлөв', choices=[], validators=[Optional()])
    submit = SubmitField('Шүүх', id="submit1", name="submit1")


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


class SupplierDateSelect(FlaskForm):
    suppliers = SelectField('Харилцагч', choices=[], validators=[InputRequired()])
    select_date = DateField('Хугацаа сонгох', validators=[InputRequired()])
    submit = SubmitField('Сонгох')

class DateSelect(FlaskForm):
    select_date = DateField('Хугацаа сонгох', validators=[Optional()])
    submit = SubmitField('Сонгох')

class SearchForm(FlaskForm):
    search_text = StringField('Хайх', validators=[InputRequired(), Length(min=2, max=50, message='Нэр 2-50 урттай')])
    submit = SubmitField('Хайх')


class CreateAccountsFromExcelForm(FlaskForm):
    excel_file = FileField('Excel файл оруулах', validators=[InputRequired(), FileAllowed(['xlsx', 'XLSX'], message='Зөвхөн Excel файл оруулна уу!')], id="inputGroupFile02")
    submit = SubmitField('Нэмэх')

class CreateProductsFromExcelForm(FlaskForm):
    suppliers = SelectField('Харилцагч', choices=[], validators=[InputRequired()])
    excel_file = FileField('Excel файл оруулах', validators=[InputRequired(), FileAllowed(['xlsx', 'XLSX'], message='Зөвхөн Excel файл оруулна уу!')], id="inputGroupFile02")
    submit = SubmitField('Нэмэх')