from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, Email, EqualTo, ValidationError, DataRequired
from webapp.database import Connection
from webapp import models
import re

class SignInForm(FlaskForm):
    email = StringField('Имэйл', validators=[DataRequired(), Email("Имэйл хаяг оруулна уу!"), Length(min=6, max=255, message='Хэт урт эсвэл богино байна!')])
    password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=6, max=255, message='Хэт богино байна!')])
    # recaptcha = RecaptchaField()
    submit = SubmitField('Нэвтрэх')

    def validate_email(self, email):
        if email.data is None:
            raise ValidationError('Имэйл хаяг оруулна уу!!!')


class SignUpForm(FlaskForm):
    company_name = StringField('Байгууллагын нэр', validators=[DataRequired()])
    firstname = StringField('Нэр', validators=[DataRequired()])
    lastname = StringField('Овог', validators=[DataRequired()])
    email = StringField('Имэйл', validators=[DataRequired(), Email(message='Имэйл хаяг оруулна уу!'), Length(min=3, max=50, message='Хэтэрхий урт байна!')])
    phone = StringField('Утасны дугаар', validators=[DataRequired()])
    password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=3, max=25)])
    confirm_password = PasswordField('Нууц үг дахин', validators=[DataRequired(), EqualTo('password', message='Нууц үгнүүд таарахгүй байна!')])
    # recaptcha = RecaptchaField()
    submit = SubmitField('Бүртгүүлэх')

    def validate_company_name(self, company_name):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((company_name.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг тоо ашиглана уу!')

        if company_name.data != company_name.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_firstname(self, firstname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((firstname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг тоо ашиглана уу!')

        if firstname.data != firstname.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

    def validate_lastname(self, lastname):
        allowed_chars = set(("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZефцужэнгшүзкъйыбөахролдпячёсмитьвюЕФЦУЖЭНГШҮЗКЪЙЫБӨАХРОЛДПЯЧЁСМИТЬВЮ"))
        validation = set((lastname.data))
        if validation.issubset(allowed_chars):
            pass
        else:
            raise ValidationError('Зөвхөн үсэг тоо ашиглана уу!')

        if lastname.data != lastname.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

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

        if phone.data != phone.data:
            raise ValidationError("Урд хойно хоосон зай ашигласан байна! Арилгана уу!")

        connection = Connection()
        account = connection.query(models.User).filter_by(phone=phone.data).first()
        connection.close()
        if account:
            raise ValidationError('Энэ утас өөр данс нь дээр бүртгэлтэй байна! Өөр утас ашиглана уу!')

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


class RequestResetForm(FlaskForm):
    email = StringField('Бүртгэлтэй имэйл хаяг', validators=[DataRequired('Имэйл оруулна уу!'), Email('Имэйл оруулна уу!')])
    submit = SubmitField('Илгээх')

    def validate_email(self, email):
        connection = Connection()
        account = connection.query(models.User).filter_by(email=email.data).first()
        connection.close()
        if account is None:
            raise ValidationError('Хэрэглэгч олдсонгүй!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Нууц үг', validators=[DataRequired(), Length(min=3, max=25)])
    confirm_password = PasswordField('Нууц үг дахин', validators=[DataRequired(), EqualTo('password', message='Нууц үгнүүд таарахгүй байна!')])
    submit = SubmitField('Нууц үгээ солих')

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