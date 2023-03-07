from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp.accountant.forms import FiltersForm, ReceivePaymentForm, DateSelect
from webapp import models
from datetime import datetime, timedelta, time
from sqlalchemy import func, or_
import calendar
from dateutil.rrule import DAILY,rrule
import pytz

accountant_payment_blueprint = Blueprint('accountant_payment', __name__)

@accountant_payment_blueprint.route('/accountant/driver/payments', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_payments():
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    
    form = FiltersForm()
    form.drivers.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form.drivers.choices.insert(0,(0,'Жолооч сонгох'))

    orders = []
    driver_orders = []
    # selected_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    # selected_date_add_time = selected_date.strftime("%Y-%m-%d %H:%M:%S")
    # datetime_object = datetime.strptime(selected_date_add_time, '%Y-%m-%d %H:%M:%S')
    # selected_date_add_time_replace = datetime_object.replace(hour=17, minute=0)
    # selected_date_time_minus_1day = selected_date_add_time_replace - timedelta(days=1)

    unprocessed_orders = connection.execute("SELECT count(delivery.id) as total_count, CONCAT(driver.lastname, ' ', driver.firstname) as driver_name FROM sunsundatabase2.delivery as delivery join sunsundatabase2.user as driver on delivery.assigned_driver_id=driver.id WHERE delivery.is_processed_by_accountant=false and delivery.is_delivered=true and delivery.status='completed' group by delivery.assigned_driver_id;").all()

    form1 = ReceivePaymentForm()

    if form.validate_on_submit():
        current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
        date1 = datetime.combine(current_date - timedelta(days=1), time(hour=17, minute=0))
        date2 = datetime.combine(current_date, time(hour=17, minute=0))
        driver_orders = connection.query(models.Delivery).\
            filter(models.Delivery.assigned_driver_id == form.drivers.data).\
            filter(models.Delivery.received_from_clerk_date.between(date1.replace(hour=17, minute=0), date2.replace(hour=17, minute=0))).order_by(models.Delivery.status.desc()).all()
        orders = connection.query(models.Delivery).filter(models.Delivery.assigned_driver_id==form.drivers.data).filter(models.Delivery.is_delivered==True).filter(models.Delivery.is_processed_by_accountant==False).filter(models.Delivery.status=="completed").all()
        # orders = connection.query(models.Delivery).join(models.User, models.Delivery.assigned_driver_id == models.User.id).filter(models.Delivery.is_processed_by_accountant == False, models.Delivery.received_from_clerk_date >= selected_date_time_minus_1day, models.Delivery.received_from_clerk_date < selected_date_add_time_replace).all()
        return render_template('/accountant/payments.html', form=form, orders=orders, form1=form1, driver_orders=driver_orders)

    if form1.validate_on_submit():
        line_order_id = request.form.getlist("order_id")
        line_order_id_values = request.form.getlist("orderIdValue")
        selected_order_total = request.form.get("ordersTotal")

        if len(line_order_id_values) > 0:
            if int(form1.total_amount.data) + int(form1.remaining_amount.data) == int(selected_order_total):
                driver_id = 0

                for i, line_order in enumerate(line_order_id_values):
                    order_to_update = connection.query(models.Delivery).get(int(line_order))
                    driver_id = order_to_update.assigned_driver_id

                    if order_to_update.is_processed_by_accountant == False:
                        order_to_update.is_processed_by_accountant = True
                        order_to_update.processed_accountant_id = current_user.id
                    else:
                        continue

                new_payment = models.Payment()
                new_payment.total_amount = form1.total_amount.data
                new_payment.remaining_amount = form1.remaining_amount.data
                new_payment.date_of_payment = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) - timedelta(hours=+24)
                new_payment.comment = form1.comment.data
                new_payment.delivery_ids = line_order_id_values
                new_payment.accountant_id = current_user.id
                new_payment.driver_id = driver_id
                new_payment.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                connection.add(new_payment)

                try:
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    flash('Алдаа гарлаа!', 'danger')
                    return redirect(url_for("accountant_payment.accountant_payments"))
                else:
                    return redirect(url_for("accountant_payment.accountant_payments"))

            else:
                flash('Нийлбэр дүн таарахгүй байна!', 'danger')
                return redirect(url_for("accountant_payment.accountant_payments"))
        else:
            if int(form1.total_amount.data) + int(form1.remaining_amount.data) == int(form1.net_amount.data):
                line_order_id = request.form.getlist("order_id")

                driver_id = 0

                for line_order in line_order_id:
                    order_to_update = connection.query(models.Delivery).get(int(line_order))
                    driver_id = order_to_update.assigned_driver_id

                    if order_to_update.is_processed_by_accountant == False:
                        order_to_update.is_processed_by_accountant = True
                        order_to_update.processed_accountant_id = current_user.id
                    else:
                        continue

                new_payment = models.Payment()
                new_payment.total_amount = form1.total_amount.data
                new_payment.remaining_amount = form1.remaining_amount.data
                new_payment.date_of_payment = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) - timedelta(hours=+24)
                new_payment.comment = form1.comment.data
                new_payment.delivery_ids = line_order_id
                new_payment.accountant_id = current_user.id
                new_payment.driver_id = driver_id
                new_payment.received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                connection.add(new_payment)

                try:
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    flash('Алдаа гарлаа!', 'danger')
                    return redirect(url_for("accountant_payment.accountant_payments"))
                else:
                    return redirect(url_for("accountant_payment.accountant_payments"))

            else:
                flash('Нийлбэр дүн таарахгүй байна!', 'danger')
                return redirect(url_for("accountant_payment.accountant_payments"))

    return render_template('/accountant/payments.html', form=form, orders=orders, form1=form1, unprocessed_orders=unprocessed_orders, driver_orders=driver_orders)


@accountant_payment_blueprint.route('/accountant/driver/payments/daily', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_payments_daily():
    connection = Connection()
    payments_daily = []
    form = DateSelect()

    if form.validate_on_submit():
        payments_daily = connection.query(models.Payment).filter(func.date(models.Payment.created_date) == form.select_date.data).all()
        return render_template('/accountant/payments_daily.html', form=form, payments_daily=payments_daily)
    return render_template('/accountant/payments_daily.html', form=form, payments_daily=payments_daily)


@accountant_payment_blueprint.route('/accountant/driver/payments/<int:payment_id>', methods=['GET', 'POST'])
@login_required
@has_role('accountant')
def accountant_payments_detail(payment_id):
    connection = Connection()
    orders = []
    payments_collection = connection.query(models.Payment).filter(models.Payment.id==payment_id).first()
    ids = payments_collection.delivery_ids
    for i in ids:
        order = connection.query(models.Delivery).get(i)
        orders.append(order)
        
    return render_template('/accountant/payment_details.html', orders=orders)


@accountant_payment_blueprint.route('/accountant/driver/payments/two-weeks', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_payments_two_weeks():
    connection = Connection()
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    payment_datas = []

    if current_date.day <= 15:
        start_day = 1
        end_day = 15
    else:
        start_day = 16
        end_day = calendar.monthrange(current_date.year, current_date.month)[1]

    for driver in drivers:
            driver_format = [f"{driver.lastname[0].capitalize()}. {driver.firstname}", driver.id]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
                day_info = connection.execute('SELECT COALESCE(sum(payment.total_amount),0) as total_amount, COALESCE(sum(payment.remaining_amount),0) as remaining_amount FROM sunsundatabase2.payment as payment where payment.driver_id=:driver_id and DATE(payment.date_of_payment)=:day;', {"day": i.date(), "driver_id": driver.id}).first()
                day_format = (i.day, int(day_info.total_amount) if day_info is not None else 0, int(day_info.remaining_amount) if day_info is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            driver_format.insert(2, (daily_data))
            payment_datas.append(driver_format)


    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():

        payment_datas = []

        if form.select_date.data.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]

        for driver in drivers:
            driver_format = [f"{driver.lastname[0].capitalize()}. {driver.firstname}", driver.id]
            daily_data = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(f'{form.select_date.data.year}-{form.select_date.data.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{form.select_date.data.year}-{form.select_date.data.month}-{end_day}', '%Y-%m-%d')):
                day_info = connection.execute('SELECT COALESCE(sum(payment.total_amount),0) as total_amount, COALESCE(sum(payment.remaining_amount),0) as remaining_amount FROM sunsundatabase2.payment as payment where payment.driver_id=:driver_id and DATE(payment.date_of_payment)=:day;', {"day": i.date(), "driver_id": driver.id}).first()
                day_format = (i.day, int(day_info.total_amount) if day_info is not None else 0, int(day_info.remaining_amount) if day_info is not None else 0)
                daily_data.append(day_format)
                days_data.append(i.day)

            driver_format.insert(2, (daily_data))
            payment_datas.append(driver_format)
        return render_template('/accountant/payments_two_week.html', form=form, payment_datas=payment_datas, current_date=current_date, day_list=days_data)
    return render_template('/accountant/payments_two_week.html', form=form, payment_datas=payment_datas, current_date=current_date, day_list=days_data)


@accountant_payment_blueprint.route('/accountant/warehouse-sales/payments', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_warehouse_sale_payments():
    connection = Connection()
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = DateSelect()
    warehouse_sales = connection.query(models.WarehouseSale).filter(func.date(models.WarehouseSale.created_date)==current_date.date()).all()

    if form.validate_on_submit() and form.select_date.data is not None:
        warehouse_sales = connection.query(models.WarehouseSale).filter(func.date(models.WarehouseSale.created_date)==form.select_date.data).all()
        return render_template('/accountant/warehouse_sales_payments.html', warehouse_sales=warehouse_sales, form=form)
    return render_template('/accountant/warehouse_sales_payments.html', warehouse_sales=warehouse_sales, form=form)


@accountant_payment_blueprint.route('/accountant/warehouse-sales/receive-payment', methods=['GET', 'POST'])
@login_required
@has_role('accountant')
def accountant_warehouse_sale_receive_payment():
    body = request.json
    connection = Connection()
    warehouse_sale = connection.query(models.WarehouseSale).filter(models.WarehouseSale.id==int(body["warehouse_sale_id"]), models.WarehouseSale.is_processed_by_accountant==False).first()

    if warehouse_sale is None:
        return jsonify({"response": False, "msg": "Олдсонгүй"}), 400

    if warehouse_sale.is_processed_by_accountant is True:
        return jsonify({"response": False, "msg": "Тооцоо хүлээж авсан байна!"}), 400

    if warehouse_sale.is_processed_by_accountant is False:
        try:
            warehouse_sale.is_processed_by_accountant = True
            warehouse_sale.accountant_id = current_user.id

            connection.commit()
        except Exception as ex:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"}), 400
        else:
            return jsonify({"response": True, "msg": "Тооцоо хийгдлээ"}), 200