from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier2.forms import OrderAddForm, OrderEditForm, DateSelectForm
from datetime import datetime, time
from sqlalchemy import func, or_
from webapp.utils import is_time_between
import pytz


initial_districts = ['Багануур', 'Багахангай', 'Баянгол', 'Баянзүрх', 'Налайх', 'Хан-Уул', 'Сүхбаатар', 'Сонгинохайрхан', 'Чингэлтэй']
initial_aimags = ['Архангай','Баян-Өлгий','Баянхонгор','Булган','Говь-Алтай','Говьсүмбэр','Дархан-Уул','Дорноговь','Дорнод','Дундговь','Завхан','Орхон','Өвөрхангай','Өмнөговь','Сүхбаатар','Сэлэнгэ','Төв','Увс','Ховд','Хөвсгөл','Хэнтий']


supplier2_order_blueprint = Blueprint('supplier2_order', __name__)


@supplier2_order_blueprint.route('/supplier2/orders', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_orders():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    orders = []
    deliveries = connection.query(models.Delivery).filter(models.Delivery.user_id == current_user.id, or_(func.date(models.Delivery.delivery_date) == cur_date.date(), func.date(models.Delivery.created_date) == cur_date.date(), (func.date(models.Delivery.postphoned_date) == cur_date.date()) & (models.Delivery.is_postphoned == True))).all()
    orders = deliveries

    form = DateSelectForm()

    if form.date.data is not None and form.validate_on_submit():
        if form.date.data > cur_date.date():
            orders = []
        elif form.date.data <= cur_date.date():
            deliveries = connection.query(models.Delivery).filter(models.Delivery.user_id == current_user.id, or_(func.date(models.Delivery.delivery_date) == form.date.data, func.date(models.Delivery.created_date) == form.date.data, (func.date(models.Delivery.postphoned_date) == form.date.data) & (models.Delivery.is_postphoned == True))).all()
            orders = deliveries

        return render_template('/supplier/supplier2/orders.html', cur_date=cur_date, orders=orders, form=form)

    return render_template('/supplier/supplier2/orders.html', cur_date=cur_date, orders=orders, form=form)


@supplier2_order_blueprint.route('/supplier2/orders/add', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_add():

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order_window = is_time_between(time(6,30), time(10,30))
    connection = Connection()

    form = OrderAddForm()
    form.district.choices = [(district) for district in initial_districts]
    form.district.choices.insert(0,'Дүүрэг сонгох')
    form.khoroo.choices = [(f'%s'%(khoroo_num+1)) for khoroo_num in range(50)]
    form.khoroo.choices.insert(0,'Хороо сонгох')
    form.aimag.choices = [(aimag) for aimag in initial_aimags]
    form.aimag.choices.insert(0,'Аймаг сонгох')

    if form.validate_on_submit():
        line_phone = request.form.getlist("phone_value")
        line_phone_more = request.form.getlist("phone_more_value")
        line_district = request.form.getlist("district_value")
        line_khoroo = request.form.getlist("khoroo_value")
        line_address = request.form.getlist("address_value")
        line_total_amount = request.form.getlist("total_amount_value")
        line_aimag = request.form.getlist("aimag_value")
        line_order_type = request.form.getlist("order_type_value")
        line_comment = request.form.getlist("comment_value")

        pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(models.PickupTask.is_ready==True).filter(models.PickupTask.is_completed==False).first()

        if pickup_task:
            for i, phone in enumerate(line_phone):
                if line_order_type[i] == "true":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.district = line_district[i]
                    pickup_task_detail.khoroo = line_khoroo[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "local"

                    pickup_task.pickup_task_details.append(pickup_task_detail)

                elif line_order_type[i] == "false":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.aimag = line_aimag[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "long"

                    pickup_task.pickup_task_details.append(pickup_task_detail)

        else:

            pickup_task = models.PickupTask()
            pickup_task.is_ready = True
            pickup_task.status = "waiting"

            current_user.pickup_tasks.append(pickup_task)
        
            for i, phone in enumerate(line_phone):
                if line_order_type[i] == "true":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.district = line_district[i]
                    pickup_task_detail.khoroo = line_khoroo[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "local"
                    pickup_task_detail.comment = line_comment[i]

                    pickup_task.pickup_task_details.append(pickup_task_detail)

                elif line_order_type[i] == "false":
                    pickup_task_detail = models.PickupTaskDetail()
                    pickup_task_detail.phone = phone
                    pickup_task_detail.phone_more = line_phone_more[i]
                    pickup_task_detail.aimag = line_aimag[i]
                    pickup_task_detail.address = line_address[i]
                    pickup_task_detail.total_amount = line_total_amount[i]
                    pickup_task_detail.destination_type = "long"
                    pickup_task_detail.comment = line_comment[i]

                    pickup_task.pickup_task_details.append(pickup_task_detail)

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier2_order.supplier2_order_add'))
        else:
            flash('Жолоочид хүлээлгэж өгөхөд бэлэн боллоо.', 'success')
            return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    return render_template('/supplier/supplier2/order_add.html', form=form, cur_date=cur_date, order_window=order_window)


@supplier2_order_blueprint.route('/supplier2/orders/cancel/<int:pickup_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_cancel(pickup_task_id):
    connection = Connection()

    pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.id==pickup_task_id, models.PickupTask.is_cancelled==False).first()

    if pickup_task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    if pickup_task.is_completed or pickup_task.is_cancelled:
        flash('Цуцлах боломжгүй. Ажил дууссан байна', 'danger')
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    if current_user.id != pickup_task.supplier_id:
        abort(403)

    try:
        pickup_task_to_cancel = connection.query(models.PickupTask).filter(models.PickupTask.id==pickup_task_id).first()
        pickup_task_to_cancel.is_ready = False
        pickup_task_to_cancel.is_cancelled = True
        pickup_task_to_cancel.status = "cancelled"
        connection.commit()
    except Exception:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))
    else:
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))


@supplier2_order_blueprint.route('/supplier2/orders/edit/<int:pickup_task_id>/<int:pickup_task_detail_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_edit(pickup_task_id, pickup_task_detail_id):

    connection = Connection()
    task = connection.query(models.PickupTask).get(pickup_task_id)
    task_detail = connection.query(models.PickupTaskDetail).get(pickup_task_detail_id)

    if task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier2_order.supplier2_orders'))

    if task_detail is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier2_order.supplier2_orders'))

    if current_user.id != task.supplier_id:
        abort(403)

    form = OrderEditForm()

    form.district.choices = [(district) for district in initial_districts]
    form.khoroo.choices = [(f'%s'%(district+1)) for district in range(50)]
    form.aimag.choices = [(aimag) for aimag in initial_aimags]

    if form.validate_on_submit():
        
        task_detail.phone = form.phone.data
        task_detail.phone_more = form.phone_more.data

        if task_detail.destination_type == "local":
            task_detail.district = form.district.data
            task_detail.khoroo = form.khoroo.data
        
        if task_detail.destination_type == "long":
            task_detail.aimag = form.aimag.data
        
        task_detail.address = form.address.data
        task_detail.total_amount = form.total_amount.data

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))
        else:
            flash('Хүргэлт өөрчлөгдлөө', 'info')
            return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    elif request.method == 'GET':
        form.phone.data = task_detail.phone
        form.phone_more.data = task_detail.phone_more
        form.district.data = task_detail.district
        form.khoroo.data = task_detail.khoroo
        form.aimag.data = task_detail.aimag
        form.address.data = task_detail.address
        form.total_amount.data = task_detail.total_amount
        return render_template('/supplier/supplier2/order_edit.html', form=form, task_detail=task_detail)

    return render_template('/supplier/supplier2/order_edit.html', form=form, task_detail=task_detail)


@supplier2_order_blueprint.route('/supplier2/orders/delete/<int:pickup_task_id>/<int:pickup_task_detail_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_order_delete(pickup_task_id, pickup_task_detail_id):

    connection = Connection()
    pickup_task = connection.query(models.PickupTask).get(pickup_task_id)
    pickup_task_detail = connection.query(models.PickupTaskDetail).get(pickup_task_detail_id)

    if pickup_task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    if pickup_task_detail is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    if current_user.id != pickup_task.supplier_id:
        abort(403)

    if pickup_task.is_completed or pickup_task.is_cancelled or pickup_task.is_driver_received:
        flash('Ажил өөрчлөх боломжгүй!', 'danger')
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    if pickup_task.status != "waiting" or pickup_task.status != "enroute":
        pickup_task.pickup_task_details.remove(pickup_task_detail)
        connection.query(models.PickupTaskDetail).filter_by(id=pickup_task_detail.id).delete()

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))
        else:
            flash('Хүргэлт өөрчлөгдлөө', 'info')
            return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))

    else:
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))
