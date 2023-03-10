from flask import (Blueprint, render_template, redirect, abort, url_for, flash)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models
from sqlalchemy import func, or_
from .forms import DeliveryStatusForm, DeliveryPostphonedForm, DeliveryCancelledForm, DateSelect, DeliveryCompletedForm
from datetime import datetime, timedelta
import pytz

driver_order_blueprint = Blueprint('driver_order', __name__)

initial_delivery_status = ['Хүргэсэн', 'Цуцалсан', 'Хойшилсон']


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


@driver_order_blueprint.route('/driver/orders')
@login_required
@has_role('driver')
def driver_orders():
    connection = Connection()
    orders = connection.query(models.Delivery).filter(models.Delivery.status == "assigned", models.Delivery.assigned_driver_id==current_user.id, models.Delivery.is_driver_received==True).order_by(models.Delivery.status.desc()).all()
    return render_template('/driver/orders.html', orders=orders)


@driver_order_blueprint.route('/driver/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_order_detail(order_id):

    connection = Connection()
    form = DeliveryStatusForm()
    form.current_status.choices = [(status) for status in initial_delivery_status]
    
    order = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != order.assigned_driver_id:
        abort(403)

    if order.is_received_from_clerk is False:
        flash('Хүлээж аваагүй байна!', 'info')
        return redirect(url_for('driver_order.driver_orders'))

    if form.validate_on_submit():
        if switch_status(form.current_status.data) == "postphoned":
            return redirect(url_for('driver_order.driver_order_postphoned', order_id=order.id))
        elif switch_status(form.current_status.data) == "cancelled":
            return redirect(url_for('driver_order.driver_order_cancelled', order_id=order.id))
        elif switch_status(form.current_status.data) == "completed":
            return redirect(url_for('driver_order.driver_order_completed', order_id=order.id))
    return render_template('/driver/order.html', order=order, form=form)


@driver_order_blueprint.route('/driver/orders/receive/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_order_receive(order_id):

    connection = Connection()

    order = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != order.assigned_driver_id:
        abort(403)

    if order.status != "assigned":
        flash('Өөрчлөх боломжгүй!', 'info')
        return redirect(url_for('driver_order.driver_orders'))

    if order.is_received_from_clerk is True:
        flash('Хүргэлтийг жолооч хүлээж авсан байна!', 'info')
        return redirect(url_for('driver_order.driver_orders'))
    else:
        try:
            order.is_received_from_clerk = True
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('driver_order.driver_orders'))
        else:
            return redirect(url_for('driver_order.driver_orders'))


@driver_order_blueprint.route('/driver/orders/completed/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_order_completed(order_id):

    connection = Connection()
    form = DeliveryCompletedForm()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != order.assigned_driver_id:
        abort(403)

    if order.status != "assigned":
        flash('Өөрчлөх боломжгүй!', 'info')
        return redirect(url_for('driver_order.driver_orders'))

    if form.validate_on_submit():
        order.status = "completed"
        order.is_delivered = True
        order.driver_comment = form.driver_comment.data
        order.delivery_attempts = order.delivery_attempts + 1
        order.delivered_date = cur_date

        if order.is_postphoned:
            if order.postphoned_date.date() > cur_date.date():
                order.postphoned_date = cur_date

        payment_detail = models.PaymentDetail()
        payment_detail.total_amount = form.received_amount.data
        payment_detail.comment = form.driver_comment.data

        order_history = models.DriverOrderHistory()
        order_history.status = "completed"
        order_history.delivery_id = order.id
        order_history.type = "delivery"
        order_history.driver_id = current_user.id
        order_history.supplier_name = order.user.company_name

        order.payment_details = payment_detail
        connection.add(order_history)

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('driver_order.driver_orders'))
        else:
            return redirect(url_for('driver_order.driver_orders'))
    
    return render_template('/driver/order_completed.html', order=order, form=form)


@driver_order_blueprint.route('/driver/orders/cancelled/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_order_cancelled(order_id):

    connection = Connection()
    form = DeliveryCancelledForm()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    order = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != order.assigned_driver_id:
        abort(403)

    if order.status != "assigned":
        flash('Өөрчлөх боломжгүй!', 'info')
        return redirect(url_for('driver_order.driver_orders'))

    if form.validate_on_submit():
        order.status = "cancelled"
        order.is_cancelled = True
        order.is_delivered = False
        order.driver_comment = form.driver_comment.data
        order.delivery_attempts = order.delivery_attempts + 1

        if order.is_postphoned:
            if order.postphoned_date.date() > cur_date.date():
                order.postphoned_date = cur_date
                order.delivery_date = cur_date

        job_history = models.DriverOrderHistory()
        job_history.created_date = cur_date
        job_history.status = "cancelled"
        job_history.driver_id = current_user.id
        job_history.type = "delivery"
        job_history.delivery_id = order.id
        job_history.supplier_name = order.user.company_name

        driver_return = models.DriverReturn()
        driver_return.delivery_status = "cancelled"
        driver_return.driver_id = current_user.id
        driver_return.delivery_id = order.id

        connection.add(driver_return)
        connection.add(job_history)

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('driver_order.driver_orders'))
        else:
            return redirect(url_for('driver_order.driver_orders'))
    
    return render_template('/driver/order_cancelled.html', order=order, form=form)


@driver_order_blueprint.route('/driver/orders/postphoned/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_order_postphoned(order_id):

    connection = Connection()
    form = DeliveryPostphonedForm()
    order = connection.query(models.Delivery).filter_by(id=order_id).first()

    if current_user.id != order.assigned_driver_id:
        abort(403)

    if order.status != "assigned":
        flash('Өөрчлөх боломжгүй!', 'info')
        return redirect(url_for('driver_order.driver_orders'))

    if form.validate_on_submit():
        tomorrow = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date() + timedelta(days=1)

        if form.postphoned_date.data < tomorrow:
            flash('Хойшлуулах өдөр буруу байна. Маргаашаас эхлэнэ. Зөв он сар өдөр сонгоно уу!', 'info')
            return render_template('/driver/order_postphoned.html', order=order, form=form)

        try:
            new_date = datetime.combine(form.postphoned_date.data, datetime.now(pytz.timezone("Asia/Ulaanbaatar")).time())
            timezone = pytz.timezone('Asia/Ulaanbaatar')
            dt_aware = timezone.localize(new_date)

            order.status = "unassigned"
            order.postphoned_driver_id = current_user.id
            order.driver_comment = form.driver_comment.data
            order.is_postphoned = True
            order.is_delivered = False
            order.delivery_attempts = order.delivery_attempts + 1
            order.is_received_from_clerk = False
            order.is_driver_received = False
            order.assigned_driver_id = None
            order.postphoned_date = dt_aware
            order.delivery_date = dt_aware

            job_history = models.DriverOrderHistory()
            job_history.status = "postphoned"
            job_history.driver_id = current_user.id
            job_history.type = "delivery"
            job_history.delivery_id = order.id
            job_history.supplier_name = order.user.company_name

            driver_return = models.DriverReturn()
            driver_return.delivery_status = "postphoned"
            driver_return.driver_id = current_user.id
            driver_return.delivery_id = order.id

            connection.add(driver_return)
            connection.add(job_history)

            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('driver_order.driver_orders'))
        else:
            return redirect(url_for('driver_order.driver_orders'))
    
    return render_template('/driver/order_postphoned.html', order=order, form=form)


@driver_order_blueprint.route('/driver/orders/history', methods=['GET', 'POST'])
@login_required
@has_role('driver')
def driver_orders_history():

    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = DateSelect()

    orders = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.driver_id==current_user.id, func.date(models.DriverOrderHistory.created_date)==cur_date.date()).all()

    if form.validate_on_submit():
        orders = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.driver_id==current_user.id, func.date(models.DriverOrderHistory.created_date)==form.select_date.data).all()
        return render_template('/driver/orders_history.html', orders=orders, form=form)

    return render_template('/driver/orders_history.html', orders=orders, form=form)

