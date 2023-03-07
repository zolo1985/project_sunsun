from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, HiddenField, RadioField, PasswordField
from wtforms.validators import ValidationError, Optional, NumberRange, InputRequired, Length, Regexp
from flask_wtf.file import FileField, FileAllowed
from webapp.database import Connection
import re
import webapp.models as models


def validate_at_least_one_property(form, field):
    if not form.color.data and not form.size.data and not form.type.data:
        raise ValidationError('Өнгө, хэмжээ, төрлийн аль нэгийг заавал бөглөх ёстой. Бараагаа дараа нь хольж андуурахгүй тулд аль их мэдээлэл оруулана уу!')


def validate_duplicate_product(form, field):
    connection = Connection()
    product = connection.query(models.Product).filter(models.Product.name == form.name.data, 
                                                        models.Product.color == form.color.data, 
                                                        models.Product.type == form.type.data, 
                                                        models.Product.size == form.size.data).first()
    if product:
        raise ValidationError('Ийм нэр, өнгө, хэмжээ, төрөлтэй бараа тань дээр бүртгэлтэй байна.')


def validate_duplicate_product_edit(form, field):
    connection = Connection()
    product = connection.query(models.Product).filter(models.Product.name == form.name.data, 
                                                        models.Product.color == form.color.data, 
                                                        models.Product.type == form.type.data, 
                                                        models.Product.size == form.size.data).all()
    if len(product)>1:
        raise ValidationError('Ийм нэр, өнгө, хэмжээ, төрөлтэй бараа тань дээр бүртгэлтэй байна.')


# def validate_duplicate_product(form, field):
#     connection = Connection()

#     filters = [models.Product.supplier_id == current_user.id]

#     if form.name.data:
#         filters.append(models.Product.name == form.name.data)

#     if form.type.data:
#         filters.append(models.Product.type == form.type.data)
#     else:
#         filters.append(or_(models.Product.type == "", models.Product.type.is_(None), models.Product.type == "Төрөлгүй"))

#     if form.size.data:
#         filters.append(models.Product.size == form.size.data)
#     else:
#         filters.append(or_(models.Product.size == "", models.Product.size.is_(None), models.Product.type == "Хэмжээгүй"))

#     if form.color.data:
#         filters.append(models.Product.color == form.color.data)
#     else:
#         filters.append(or_(models.Product.color == "", models.Product.color.is_(None), models.Product.type == "Өнгөгүй"))

#     product = connection.query(models.Product).filter(*filters).first()
#     if product:
#         raise ValidationError('Ийм нэр, өнгө, хэмжээ, төрөлтэй бараа тань дээр бүртгэлтэй байна.')


class FiltersForm(FlaskForm):
    date = DateField('Он сараар', validators=[Optional()])
    submit = SubmitField('Шүүх')

    def validate_date(self, date):
        if date.data is None:
            raise ValidationError("Он сар өдөр сонгоно уу!")


class OrderAddForm(FlaskForm):
    order_type = RadioField('Хүргэлтийн чиглэл', choices=[(0,'Улаанбаатар'),(1,'Орон нутаг')], validators=[Optional()], default=0)
    phone = StringField('Утасны дугаар',validators=[ InputRequired(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    phone_more = StringField('Нэмэлт утасны дугаар*. (Заавал биш)',validators=[Optional(), Regexp(regex=r"^\d{8}$", message='Зөвхөн тоо ашиглана уу!'), Length(min=8, max=8, message='Орон дутуу байна!')])
    district = SelectField('Дүүрэг', choices=[], validators=[Optional()])
    khoroo = SelectField('Хороо', choices=[], validators=[Optional()])
    aimag = SelectField('Аймаг', choices=[], validators=[Optional()])
    address = TextAreaField('Хаяг', validators=[InputRequired()])
    total_amount = IntegerField('Үйлчлүүлэгчээс авах дүн', validators=[InputRequired(), NumberRange(min=0)], default=0)
    submit = SubmitField('Хүргэлт үүсгэх')


class OrderDetailFileAddForm(FlaskForm):
    excel_file = FileField('Excel файл оруулах', validators=[InputRequired(), FileAllowed(['xlsx', 'XLSX'], message='Зөвхөн Excel файл оруулна уу!')], id="inputGroupFile02")
    preview_orders = SubmitField('Захиалгууд харах')
    

class SubmitFileOrders(FlaskForm):
    submit = SubmitField('Захиалгууд нэмэх')


class ProductAddForm(FlaskForm):
    name = StringField('Нэр', validators=[InputRequired(), validate_at_least_one_property, validate_duplicate_product])
    color = StringField('Өнгө', validators=[Optional(), validate_duplicate_product])
    size = StringField('Хэмжээ', validators=[Optional(), validate_duplicate_product])
    type = StringField('Төрөл', validators=[Optional(), validate_duplicate_product])
    description = TextAreaField('Бусад', validators=[Optional()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[InputRequired(), NumberRange(min=1)], id='price', default=0)
    usage_guide = TextAreaField('Хэрэглэх заавар', validators=[Optional()])
    submit = SubmitField('Бараа бүртгэлд нэмэх')


class ProductEditForm(FlaskForm):
    name = StringField('Нэр', validators=[InputRequired(), validate_at_least_one_property, validate_duplicate_product_edit])
    color = StringField('Өнгө', validators=[Optional(), validate_duplicate_product_edit])
    size = StringField('Хэмжээ', validators=[Optional(), validate_duplicate_product_edit])
    type = StringField('Төрөл', validators=[Optional(), validate_duplicate_product_edit])
    description = TextAreaField('Бусад', validators=[Optional()])
    image = FileField('Зураг', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], message='Зөвхөн jpg, jpeg, png өргөтгөлтэй зураг оруулна уу!')], id='image')
    price = IntegerField('Үнэ', validators=[InputRequired(), NumberRange(min=1)], id='price', default=0)
    usage_guide = TextAreaField('Хэрэглэх заавар', validators=[Optional()])
    submit = SubmitField('Өөрчлөх')


class InventoryAddForm(FlaskForm):
    quantity = IntegerField('Тоо ширхэг', validators=[InputRequired(), NumberRange(min=1)], id='quantity', default=0)
    product = SelectField('Бараа', choices=[],validators=[InputRequired()])
    submit = SubmitField('Хүлээлгэж өгөх')


class DriverPickupForm(FlaskForm):
    date = DateField('Хугацаа сонгох', validators=[InputRequired()])
    submit = SubmitField('Өдрөөр хайх')


class InventoryPickupAddForm(FlaskForm):
    quantity = IntegerField('Тоо ширхэг', validators=[InputRequired(), NumberRange(min=1)], id='quantity', default=0)
    product = SelectField('Бараа', choices=[],validators=[InputRequired()])
    submit = SubmitField('Жолооч дуудах')


class ChooseType(FlaskForm):
    delivery_type = RadioField('Төрөл', choices=[(0,'Жолооч дуудах'),(1,'Агуулахад хүлээлгэж')], validators=[Optional()], default=0)
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
    search_types = SelectField('Төрөл', choices=['Хүргэлт', 'Агуулах'], validators=[InputRequired()])
    submit = SubmitField('Хайх')