from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.admin.forms import FiltersForm
from datetime import datetime
from sqlalchemy import func, or_
from sqlalchemy.sql.expression import case
import pytz


admin_order_blueprint = Blueprint('admin_order', __name__)


initial_delivery_status = ['Хувиарлагдаагүй', 'Хувиарласан', 'Хүргэсэн', 'Цуцалсан', 'Хойшилсон']
order_edit_order_status = ['Цуцлах']
initial_delivery_regions = ['Хойд', 'Урд', 'Зүүн', 'Баруун', 'Баруун Хойд', 'Зүүн Хойд', 'Баруун Урд', 'Зүүн Урд']
initial_districts = ['Багануур', 'Багахангай', 'Баянгол', 'Баянзүрх', 'Налайх', 'Хан-Уул', 'Сүхбаатар', 'Сонгинохайрхан', 'Чингэлтэй']
initial_aimags = ['Архангай','Баян-Өлгий','Баянхонгор','Булган','Говь-Алтай','Говьсүмбэр','Дархан-Уул','Дорноговь','Дорнод','Дундговь','Завхан','Орхон','Өвөрхангай','Өмнөговь','Сүхбаатар','Сэлэнгэ','Төв','Увс','Ховд','Хөвсгөл','Хэнтий']
initial_status = ['Цуцалсан', 'Хүргэсэн']

def switch_status(status):
    if status == "Хувиарласан":
        return "assigned"
    elif status == "Хүргэсэн":
        return "completed"
    elif status == "Цуцалсан":
        return "cancelled"
    elif status == "Хойшилсон":
        return "postphoned"
    elif status == "Хувиарлагдаагүй":
        return "unassigned"

def switch_stat(stat):
    if stat == "Хувиарлагдсан":
        return "assigned"
    elif stat == "Хүргэсэн":
        return "completed"
    elif stat == "Цуцалсан":
        return "cancelled"
    elif stat == "Хойшлуулсан":
        return "postphoned"
    elif stat == "Хувиарлагдаагүй":
        return "unassigned"

def switch_reverse_status(status):
    if status == "assigned":
        return "Хувиарлагдсан"
    elif status == "completed":
        return "Хүргэсэн"
    elif status == "cancelled":
        return "Цуцалсан"
    elif status == "postphoned":
        return "Хойшлуулсан"
    elif status == "unassigned":
        return "Хувиарлагдаагүй"

@admin_order_blueprint.route('/admin/orders', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_orders():
    
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    current_date = func.date(cur_date)

    orders = connection.query(models.Delivery).filter(or_(func.date(models.Delivery.delivery_date) == current_date, (func.date(models.Delivery.postphoned_date) == current_date), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))).all()


    # total_orders_count_by_driver = connection.query(func.count(models.Delivery.assigned_driver_id).label('total_count'), models.User.firstname.label('driver')) \
    #     .join(models.User, models.Delivery.assigned_driver_id == models.User.id) \
    #     .filter(func.date(models.Delivery.delivery_date) == current_date) \
    #     .group_by(models.Delivery.assigned_driver_id, models.User.firstname) \
    #     .having(func.count(models.Delivery.assigned_driver_id) > 0) \
    #     .order_by(func.count(models.Delivery.assigned_driver_id).desc()).all()

    total_orders_count_by_driver = connection.query(func.sum(case([(models.Delivery.assigned_driver_id != None, 1), (models.Delivery.postphoned_driver_id != None, 1)], else_=0))\
        .label('total_count'), models.User.firstname.label('driver'))\
        .join(models.User, or_(models.Delivery.assigned_driver_id == models.User.id, models.Delivery.postphoned_driver_id == models.User.id))\
        .filter(or_(func.date(models.Delivery.delivery_date) == current_date, func.date(models.Delivery.created_date) == current_date))\
        .group_by(models.User.firstname)\
        .having(func.sum(case([(models.Delivery.assigned_driver_id != None, 1), (models.Delivery.postphoned_driver_id != None, 1)], else_=0)) > 0)\
        .order_by(func.sum(case([(models.Delivery.assigned_driver_id != None, 1), (models.Delivery.postphoned_driver_id != None, 1)], else_=0))\
        .desc()).all()

    total_orders_count_by_district = connection.query(func.count(models.Address.district).label('total_count'), models.Address.district) \
        .join(models.Delivery, models.Delivery.id == models.Address.delivery_id) \
        .filter(or_(func.date(models.Delivery.delivery_date) == current_date, (func.date(models.Delivery.postphoned_date) == current_date), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))) \
        .group_by(models.Address.district) \
        .having(func.count(models.Address.district) > 0) \
        .order_by(models.Address.district)
    
    total_orders_count_by_aimag = connection.query(func.count(models.Address.aimag).label('total_count'), models.Address.aimag) \
        .join(models.Delivery, models.Delivery.id == models.Address.delivery_id) \
        .filter(or_(func.date(models.Delivery.delivery_date) == current_date, (func.date(models.Delivery.postphoned_date) == current_date), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))) \
        .group_by(models.Address.aimag) \
        .having(func.count(models.Address.aimag) > 0) \
        .order_by(models.Address.aimag)

    total_orders = connection.query(func.count().label('total_orders')).filter(or_(func.date(models.Delivery.delivery_date) == current_date, (func.date(models.Delivery.postphoned_date) == current_date), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))).scalar()

    unassigned_orders = connection.query(func.count().label('unassigned_orders')) \
        .filter((func.date(models.Delivery.delivery_date) == current_date), models.Delivery.status=="unassigned") \
        .scalar()

    delivered_orders = connection.query(func.count().label('delivered_orders')) \
        .filter(or_((func.date(models.Delivery.delivery_date) == current_date), (func.date(models.Delivery.postphoned_date) == current_date)), models.Delivery.status=="completed", models.Delivery.is_delivered==True) \
        .scalar()

    postphoned_orders = connection.query(func.count().label('postphoned_orders')) \
        .filter(models.Delivery.status=="unassigned", models.Delivery.is_postphoned==True) \
        .scalar()

    cancelled_orders = connection.query(func.count().label('cancelled_orders')) \
        .filter((func.date(models.Delivery.delivery_date) == current_date), models.Delivery.status=="cancelled", models.Delivery.is_cancelled==True) \
        .scalar()

    form = FiltersForm()

    if form.validate_on_submit():
        if form.date.data is not None:
            orders = connection.query(models.Delivery).filter(or_(func.date(models.Delivery.delivery_date) == form.date.data, (func.date(models.Delivery.postphoned_date) == form.date.data), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))).all()
        else:
            return redirect(url_for('admin_order.admin_orders'))

    return render_template('/admin/orders.html', orders=orders, form=form, total_orders_count_by_district=total_orders_count_by_district, total_orders_count_by_driver=total_orders_count_by_driver, total_orders_count_by_aimag=total_orders_count_by_aimag, cur_date=cur_date, unassigned_orders=unassigned_orders, total_orders=total_orders, delivered_orders=delivered_orders, postphoned_orders=postphoned_orders, cancelled_orders=cancelled_orders)