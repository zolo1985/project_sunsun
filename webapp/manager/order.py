from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import OrderEditForm, AssignRegionAndDriverForm, DriversSelect, DriversHistoriesForm, FilterDateForm, ShowCommentStatusForm, OrderAddForm, SelectDriverForm, UnassignForm, DateFilterForm
from datetime import datetime
from sqlalchemy import func, or_
from sqlalchemy.sql.expression import case
import pytz

manager_order_blueprint = Blueprint('manager_order', __name__)

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

@manager_order_blueprint.route('/manager/orders', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_orders():
    
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    current_date = func.date(cur_date)

    orders = connection.query(models.Delivery).filter(or_(func.date(models.Delivery.delivery_date) == current_date, (func.date(models.Delivery.postphoned_date) == current_date), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))).all()

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

    form = DateFilterForm()

    if form.validate_on_submit():
        if form.date.data is not None:
            orders = connection.query(models.Delivery).filter(or_(func.date(models.Delivery.delivery_date) == form.date.data, (func.date(models.Delivery.postphoned_date) == form.date.data), (func.date(models.Delivery.created_date) == current_date) & (models.Delivery.is_postphoned == True))).all()
        else:
            return redirect(url_for('manager_order.manager_orders'))

    return render_template('/manager/orders.html', orders=orders, form=form, total_orders_count_by_district=total_orders_count_by_district, total_orders_count_by_driver=total_orders_count_by_driver, total_orders_count_by_aimag=total_orders_count_by_aimag, cur_date=cur_date, unassigned_orders=unassigned_orders, total_orders=total_orders, delivered_orders=delivered_orders, postphoned_orders=postphoned_orders, cancelled_orders=cancelled_orders)


@manager_order_blueprint.route('/manager/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_detail(order_id):
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    form = OrderEditForm()

    form.select_drivers.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    form.select_regions.choices = [delivery_region for delivery_region in initial_delivery_regions]
    form.select_regions.choices.insert(0,('Бүс сонгох'))
    form.status.choices = [status for status in initial_status]
    form.status.choices.insert(0,('Төлөв сонгох'))
    form.district.choices = [(district) for district in initial_districts]
    form.district.choices.insert(0,'Дүүрэг сонгох')
    form.khoroo.choices = [(f'%s'%(district+1)) for district in range(50)]
    form.khoroo.choices.insert(0,'Хороо сонгох')
    form.aimag.choices = [(aimag) for aimag in initial_aimags]
    form.aimag.choices.insert(0,'Аймаг сонгох')
    order = connection.query(models.Delivery).filter_by(id=order_id).first()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    if order is None:
        flash('Хүргэлт олдсонгүй', 'danger')
        return redirect(url_for('manager_order.manager_orders_drivers_histories'))

    if request.method == 'POST' and form.validate_on_submit():

        if form.select_drivers.data != "0":
            order.assigned_driver_id = int(form.select_drivers.data)

        if form.select_regions.data != "Бүс сонгох":
            order.region = form.select_regions.data

        if form.district.data != "Дүүрэг сонгох":
            order.addresses.district = form.district.data

        if form.khoroo.data != "Хороо сонгох":
            order.addresses.khoroo = form.khoroo.data

        if form.aimag.data != "Аймаг сонгох":
            order.addresses.aimag = form.aimag.data

        order.addresses.address = form.address.data

        if form.total_amount.data != order.total_amount:
            if order.is_delivered is False:
                order.total_amount = form.total_amount.data
            else:
                order.total_amount = form.total_amount.data
                order.payment_details.total_amount = form.total_amount.data

        order.driver_comment = form.driver_comment.data
        order.comment = form.comment.data

        if form.delivery_date.data is not None:
            order.delivery_date = form.delivery_date.data

        if form.postphoned_date.data is not None:
            order.postphoned_date = form.postphoned_date.data

        if form.status.data != switch_reverse_status(order.status) or form.status.data != "Төлөв сонгох":
            if switch_stat(form.status.data) == "completed":
                if order.status == "unassigned":
                    flash('Хувиарлагдаагүй хүргэлт хүргэсэн төлөвт шилжүүлэх боломжгүй. Заавал хувиарласан байх шаардлагатай!', 'info')
                    return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))
                elif order.status == "assigned":
                    order.status = "completed"
                    order.is_delivered = True
                    order.driver_comment = "Менежер өөрчилсөн"
                    order.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    if order.is_postphoned:
                        if order.postphoned_date.date() > cur_date.date():
                            order.postphoned_date = cur_date

                    payment_detail = models.PaymentDetail()
                    payment_detail.total_amount = order.total_amount
                    payment_detail.comment = "Менежер өөрчилсөн"
                    order.payment_details = payment_detail

                    if order.is_driver_received:
                        job_history = models.DriverOrderHistory()
                        job_history.status = "completed"
                        job_history.delivery_id = order.id
                        job_history.type = "delivery"
                        job_history.driver_id = order.assigned_driver_id
                        job_history.supplier_name = order.user.company_name
                        connection.add(job_history)

                elif order.status == "cancelled":
                    if order.assigned_driver_id is None:
                        flash('Жолооч хувиарлагдаагүй байна. Эхлээд жолоочид хувиарлана уу!', 'info')
                        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

                    is_inventory_returned = connection.query(models.DriverReturn).filter(models.DriverReturn.delivery_id==order.id).first()

                    if is_inventory_returned.is_returned is False:
                        order.status = "completed"
                        order.is_delivered = True
                        order.is_cancelled = False
                        order.driver_comment = "Менежер өөрчилсөн"
                        order.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                        if order.is_postphoned:
                            if order.postphoned_date.date() > cur_date.date():
                                order.postphoned_date = cur_date

                        payment_detail = models.PaymentDetail()
                        payment_detail.total_amount = order.total_amount
                        payment_detail.comment = "Менежер өөрчилсөн"
                        order.payment_details = payment_detail

                        if order.is_driver_received:
                            job_history = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.delivery_id==order.id).first()
                            job_history.status = "completed"
                            job_history.driver_id = order.assigned_driver_id
                            job_history.type = "delivery"
                            job_history.delivery_id = order.id
                            job_history.supplier_name = order.user.company_name
                            connection.add(job_history)

                        connection.query(models.DriverReturn).filter(models.DriverReturn.delivery_id==order.id).delete()

                    else:
                        flash('Барааг няравт буцаасан байна. Өөрчлөх боломжгүй.', 'info')
                        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

            elif switch_stat(form.status.data) == "cancelled":
                if order.status == "unassigned":
                    if order.is_postphoned:
                        if order.postphoned_date.date() > cur_date.date():
                            order.postphoned_date = cur_date

                    if order.status == "unassigned" and order.is_postphoned:
                        job_history = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.delivery_id==order.id, models.DriverOrderHistory.type=="delivery", models.DriverOrderHistory.status=="completed").first()
                        if job_history:
                            job_history.status = "cancelled"

                        driver_return = connection.query(models.DriverReturn).filter(models.DriverReturn.delivery_id==order.id, models.DriverReturn.delivery_status=="postphoned").first()
                        if driver_return:
                            driver_return.delivery_status = "cancelled"

                    order.status = "cancelled"
                    order.is_cancelled = True
                    order.is_delivered = False
                    order.is_manager_cancelled = True
                    order.driver_comment = "Менежер өөрчилсөн"

                elif order.status == "assigned":
                    order.status = "completed"
                    order.is_delivered = True
                    order.driver_comment = "Менежер өөрчилсөн"
                    order.delivered_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                    if order.is_postphoned:
                        if order.postphoned_date.date() > cur_date.date():
                            order.postphoned_date = cur_date

                    payment_detail = models.PaymentDetail()
                    payment_detail.total_amount = order.total_amount
                    payment_detail.comment = "Менежер өөрчилсөн"
                    order.payment_details = payment_detail

                    if order.is_driver_received:
                        job_history = models.DriverOrderHistory()
                        job_history.status = "completed"
                        job_history.delivery_id = order.id
                        job_history.type = "delivery"
                        job_history.driver_id = order.assigned_driver_id
                        job_history.supplier_name = order.user.company_name
                        connection.add(job_history)

                    if order.supplier_type == "stored":
                        for detail in order.delivery_details:
                            product = connection.query(models.Product).filter(models.Product.id == detail.product_id).first()
                            product.inventory.add_items(detail.quantity, current_user.id)

                            inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.inventory_id==product.inventory.id, models.InventoryTransaction.delivery_id==order.id).first()
                            inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

                    elif order.supplier_type == "unstored":
                        print("restore unstored inventory")

                elif order.status == "completed":
                    if order.is_processed_by_accountant:
                        flash('Хүргэлт өөрчлөх боломжгүй. Нягтлан тооцоо хийсэн байна!', 'info')
                        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))
                    else:
                        order.status = "cancelled"
                        order.is_cancelled = True
                        order.is_delivered = False
                        order.is_manager_cancelled = True
                        order.driver_comment = "Менежер өөрчилсөн"
                        order.delivered_date = None

                        if order.is_postphoned:                            
                            if order.postphoned_date.date() > cur_date.date():
                                order.postphoned_date = cur_date

                        if order.is_driver_received:
                            job_history = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.delivery_id==order.id, models.DriverOrderHistory.type=="delivery", models.DriverOrderHistory.status=="completed").first()
                            job_history.status = "cancelled"

                        if order.is_received_from_clerk:
                            driver_return = models.DriverReturn()
                            driver_return.delivery_status = "cancelled"
                            driver_return.driver_id = order.assigned_driver_id
                            driver_return.delivery_id = order.id

                            connection.add(driver_return)

                        connection.query(models.PaymentDetail).filter(models.PaymentDetail.delivery_id==order.id).delete()
                        
        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))
        else:
            flash('Өөрчлөгдлөө', 'success')
            return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    elif request.method == 'GET':
        form.total_amount.data = order.total_amount
        form.status.data = switch_reverse_status(order.status)
        if order.destination_type == 'local':
            form.district.data = order.addresses.district
            form.khoroo.data = order.addresses.khoroo
        elif order.destination_type == 'long':
            form.aimag.data = order.addresses.aimag
        form.address.data = order.addresses.address
        form.phone.data = order.addresses.phone
        form.driver_comment.data = order.driver_comment
        form.comment.data = order.comment
        form.instruction.data = order.instruction

    return render_template('/manager/order.html', order=order, form=form)


@manager_order_blueprint.route('/manager/orders/region', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_assign_region():
    connection = Connection()

    current_date = func.date(datetime.now(pytz.timezone("Asia/Ulaanbaatar")))
    
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    orders1 = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == current_date).filter(models.Delivery.status == "unassigned").filter(models.Delivery.destination_type == "local").order_by(models.Address.district).all()
    long_destination_orders = connection.query(models.Delivery).join(models.Address).filter(func.date(models.Delivery.delivery_date) == current_date).filter(models.Delivery.status == "unassigned").filter(models.Delivery.destination_type == "long").order_by(models.Address.aimag).all()
    orders = orders1 + long_destination_orders

    total_orders_count_by_district = connection.query(func.count(models.Address.district).label('total_count'), models.Address.district) \
        .join(models.Delivery, models.Delivery.id == models.Address.delivery_id) \
        .filter(or_(func.date(models.Delivery.delivery_date) == current_date)) \
        .group_by(models.Address.district) \
        .having(func.count(models.Address.district) > 0) \
        .order_by(models.Address.district)

    total_orders_count_by_driver = connection.query(func.sum(case([(models.Delivery.assigned_driver_id != None, 1), (models.Delivery.postphoned_driver_id != None, 1)], else_=0))\
        .label('total_count'), models.User.firstname.label('driver'))\
        .join(models.User, or_(models.Delivery.assigned_driver_id == models.User.id, models.Delivery.postphoned_driver_id == models.User.id))\
        .filter(or_(func.date(models.Delivery.delivery_date) == current_date, func.date(models.Delivery.created_date) == current_date))\
        .group_by(models.User.firstname)\
        .having(func.sum(case([(models.Delivery.assigned_driver_id != None, 1), (models.Delivery.postphoned_driver_id != None, 1)], else_=0)) > 0)\
        .order_by(func.sum(case([(models.Delivery.assigned_driver_id != None, 1), (models.Delivery.postphoned_driver_id != None, 1)], else_=0))\
        .desc()).all()

    # total_orders_count_by_driver = connection.query(func.count(models.Delivery.assigned_driver_id).label('total_count'), models.User.firstname.label('driver')) \
    #     .join(models.User, models.Delivery.assigned_driver_id == models.User.id) \
    #     .filter(func.date(models.Delivery.delivery_date) == current_date) \
    #     .group_by(models.Delivery.assigned_driver_id, models.User.firstname) \
    #     .having(func.count(models.Delivery.assigned_driver_id) > 0) \
    #     .order_by(func.count(models.Delivery.assigned_driver_id).desc())

    total_orders_count_by_aimag = connection.query(func.count(models.Address.aimag).label('total_count'), models.Address.aimag) \
        .join(models.Delivery, models.Delivery.id == models.Address.delivery_id) \
        .filter((func.date(models.Delivery.delivery_date) == current_date)) \
        .group_by(models.Address.aimag) \
        .having(func.count(models.Address.aimag) > 0) \
        .order_by(models.Address.aimag)
    
    form = AssignRegionAndDriverForm()
    form.select_regions.choices = [(delivery_region) for delivery_region in initial_delivery_regions]
    form.select_drivers.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))

    if form.validate_on_submit():
        line_order_id = request.form.getlist("order_id")
        line_order_id_values = request.form.getlist("order_id_value")

        if form.select_drivers.data == "0":
            if len(line_order_id) <= 0:
                    return redirect(url_for('manager_order.manager_order_assign_region'))

            if len(line_order_id_values) > 0:
                for i, order_id in enumerate(line_order_id_values):
                    order = connection.query(models.Delivery).get(order_id)
                    order.region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.status = "unassigned"

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    connection.close()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    connection.close()
                    flash('Бүсчлэгдлээ.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

            else: 
                for i, order_id in enumerate(line_order_id):
                    order = connection.query(models.Delivery).get(order_id)
                    order.region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.status = "unassigned"

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    flash('Бүсчлэгдлээ.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

        elif form.select_drivers.data != "0":

            if len(line_order_id) <= 0:
                return redirect(url_for('manager_order.manager_order_assign_region'))

            if len(line_order_id_values) > 0:
                for i, order_id in enumerate(line_order_id_values):
                    order = connection.query(models.Delivery).get(order_id)
                    order.region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_id = form.select_drivers.data
                    order.status = "assigned"

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    flash('Бүс, жолооч хувиарлагдлаа.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

            else:
                for i, order_id in enumerate(line_order_id):
                    order = connection.query(models.Delivery).get(order_id)
                    order.region = form.select_regions.data
                    order.assigned_manager_id = current_user.id
                    order.assigned_driver_id = form.select_drivers.data
                    order.status = "assigned"

                try:
                    connection.commit()
                except Exception as ex:
                    flash('Алдаа гарлаа', 'danger')
                    connection.rollback()
                    return redirect(url_for('manager_order.manager_order_assign_region'))
                else:
                    flash('Бүс, жолооч хувиарлагдлаа.', 'success')    
                    return redirect(url_for('manager_order.manager_order_assign_region'))

    return render_template('/manager/assign_regions_and_drivers.html', orders=orders, total_orders_count_by_district=total_orders_count_by_district, form=form, total_orders_count_by_driver=total_orders_count_by_driver, total_orders_count_by_aimag=total_orders_count_by_aimag)


@manager_order_blueprint.route('/manager/commented/orders', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_commented_orders():

    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivered_date) == cur_date.date(), models.Delivery.driver_comment!=None, models.Delivery.show_comment==False).all()

    form = FilterDateForm()
    form1 = ShowCommentStatusForm()

    if form.validate_on_submit() and form.date.data is not None:
        orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivered_date) == form.date.data, models.Delivery.driver_comment!=None).all()
        return render_template('/manager/orders_comments.html', form=form, orders=orders, cur_date=cur_date, form1=form1)

    if form1.validate_on_submit():
        orders = connection.query(models.Delivery).filter(models.Delivery.show_status==False).all()

        for order in orders:
            order.show_status = True
            order.show_comment = True

        try:
            connection.commit()
        except Exception as ex:
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('manager_order.manager_commented_orders'))
        else:
            flash('Бүх хүргэлтйин төлөв, комментууд харилцагчид харагддаг боллоо.', 'success')    
            return redirect(url_for('manager_order.manager_commented_orders'))

    return render_template('/manager/orders_comments.html', form=form, orders=orders, cur_date=cur_date, form1=form1)


@manager_order_blueprint.route('/manager/orders/add', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_order_add():
    connection = Connection()
    suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()

    form = OrderAddForm()

    form.suppliers.choices = [(supplier.id, supplier.company_name) for supplier in suppliers]
    form.suppliers.choices.insert(0, (0,'Харилцагч сонгох'))
    form.district.choices = [(district) for district in initial_districts]
    form.district.choices.insert(0,'Дүүрэг сонгох')
    form.khoroo.choices = [(f'%s'%(district+1)) for district in range(50)]
    form.khoroo.choices.insert(0,'Хороо сонгох')
    form.aimag.choices = [(aimag) for aimag in initial_aimags]
    form.aimag.choices.insert(0,'Аймаг сонгох')

    if form.validate_on_submit():
        line_suppliers = request.form.getlist("supplier")
        line_products = request.form.getlist("product")
        line_quantities = request.form.getlist("quantity")

        if form.delivery_type.data == "0" and form.supplier_type.data == "0":
            # local delivery
            try:
                supplier = connection.query(models.User).filter(models.User.id==line_suppliers[0]).first()

                order = models.Delivery()
                order.status = "unassigned"
                order.destination_type = "local"
                order.supplier_type = "stored"
                order.is_manager_created = True
                order.total_amount = form.total_amount.data
                order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                supplier.deliveries.append(order)
                connection.flush()

                address = models.Address()
                address.phone = form.phone.data
                address.phone_more = form.phone_more.data
                address.district = form.district.data
                address.khoroo = form.khoroo.data
                address.address = form.address.data

                order.addresses = address

                for i, product in enumerate(line_products):
                    order_detail = models.DeliveryDetail()
                    order_detail.quantity = int(line_quantities[i])
                    order_detail.product_id = int(line_products[i])

                    is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(line_products[i])).first()

                    if is_detail:
                        is_detail.quantity = is_detail.quantity + int(line_quantities[i])
                    else:
                        order.delivery_details.append(order_detail)
                        connection.flush()

                    product = connection.query(models.Product).filter(models.Product.id == int(line_products[i])).first()
                    product.inventory.subtract_items(int(line_quantities[i]))

                    transaction = models.InventoryTransaction(
                        inventory=product.inventory,
                        quantity=line_quantities[i],
                        transaction_type='delivery subtraction',
                        delivery_id = order.id)
                    product.inventory.transactions.append(transaction)

                connection.commit()
            except Exception as ex:
                flash(f'Алдаа гарлаа! {ex}', 'danger')
                connection.rollback()
                return redirect(url_for('manager_order.manager_order_add'))
            else:
                flash('Хүргэлт нэмэгдлээ.', 'success')
                return redirect(url_for('manager_order.manager_order_add'))

        elif form.delivery_type.data == "0" and form.supplier_type.data == "1":
            # long delivery
            supplier = connection.query(models.User).filter(models.User.id==line_suppliers[0]).first()

            order = models.Delivery()
            order.status = "unassigned"
            order.destination_type = "long"
            order.supplier_type = "stored"
            order.is_manager_created = True
            order.total_amount = form.total_amount.data
            order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            supplier.deliveries.append(order)
            connection.flush()

            address = models.Address()
            address.phone = form.phone.data
            address.phone_more = form.phone_more.data
            address.aimag = form.aimag.data
            address.address = form.address.data

            order.addresses = address

            for i, product in enumerate(line_products):
                order_detail = models.DeliveryDetail()
                order_detail.quantity = int(line_quantities[i])
                order_detail.product_id = int(line_products[i])

                is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(line_products[i])).first()

                if is_detail:
                    is_detail.quantity = is_detail.quantity + int(line_quantities[i])
                else:
                    order.delivery_details.append(order_detail)
                    connection.flush()

                product = connection.query(models.Product).filter(models.Product.id == int(line_products[i])).first()
                product.inventory.subtract_items(int(line_quantities[i]))

                transaction = models.InventoryTransaction(
                    inventory=product.inventory,
                    quantity=line_quantities[i],
                    transaction_type='delivery subtraction',
                    delivery_id = order.id)
                product.inventory.transactions.append(transaction)

            try:
                connection.commit()
            except Exception as ex:
                flash(f'Алдаа гарлаа! {ex}', 'danger')
                connection.rollback()
                return redirect(url_for('manager_order.manager_order_add'))
            else:
                flash('Хүргэлт нэмэгдлээ.', 'success')
                return redirect(url_for('manager_order.manager_order_add'))

        elif form.delivery_type.data == "1":
            # warehouse
            try:
                supplier = connection.query(models.User).filter(models.User.id==line_suppliers[0]).first()

                new_warehouse_sale = models.WarehouseSale()
                new_warehouse_sale.is_ready = True
                new_warehouse_sale.supplier_id = supplier.id

                current_user.manager_warehouse_sales.append(new_warehouse_sale)
                connection.flush()

                for i, product in enumerate(line_products):
                    warehouse_sale_detail = models.WarehouseSaleDetail()
                    warehouse_sale_detail.quantity = int(line_quantities[i])
                    warehouse_sale_detail.product_id = int(line_products[i])

                    is_warehouse_detail = connection.query(models.WarehouseSaleDetail).filter(models.WarehouseSaleDetail.warehouse_sale_id==new_warehouse_sale.id, models.DeliveryDetail.product_id==int(line_products[i])).first()

                    if is_warehouse_detail:
                        is_warehouse_detail.quantity = is_warehouse_detail.quantity + int(line_quantities[i])
                    else:
                        new_warehouse_sale.warehouse_sale_details.append(warehouse_sale_detail)
                        connection.flush()

                    product = connection.query(models.Product).filter(models.Product.id == int(line_products[i])).first()
                    product.inventory.subtract_items(int(line_quantities[i]))

                    transaction = models.InventoryTransaction(
                        inventory=product.inventory,
                        quantity=line_quantities[i],
                        transaction_type='warehouse sale subtraction')
                    product.inventory.transactions.append(transaction) 

                payment_detail = models.PaymentDetail()
                payment_detail.total_amount = int(request.form.get("totalInput"))
                payment_detail.comment = request.form.get("commentInput")
                payment_detail.warehouse_sale_id = new_warehouse_sale.id
                new_warehouse_sale.comment = "СҮН СҮН агуулах"
                new_warehouse_sale.total_amount = int(request.form.get("totalInput"))
                connection.add(payment_detail)
            
                connection.commit()
            except Exception as ex:
                flash(f'Алдаа гарлаа! {ex}', 'danger')
                connection.rollback()
                return redirect(url_for('manager_order.manager_order_add'))
            else:
                flash('Агуулахаас захиалга үүслээ.', 'success')
                return redirect(url_for('manager_order.manager_order_add'))

        return render_template('/manager/order_add.html', form=form)

    return render_template('/manager/order_add.html', form=form)


@manager_order_blueprint.route("/manager/orders/search/products/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_search_products(supplier_id):
    query = request.form.get("term")
    connection = Connection()
    search = "%{}%".format(query)
    products = connection.query(models.Product).filter(models.Product.supplier_id==supplier_id, models.Product.name.like(search)).all()
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'color': "өнгөгүй" if product.color is None else product.color,
            'size': "хэмжээгүй" if product.size is None else product.size,
            'type': "төрөлгүй" if product.type is None else product.type,
            'quantity': product.inventory.get_items(),
            'price': int(product.price),
        })
    return jsonify(results)


@manager_order_blueprint.route("/manager/orders/assigned", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_unassign_orders():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    orders = []
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "driver")).filter_by(is_authorized = True).all()
    form = SelectDriverForm()
    form.selected_driver.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form1 = UnassignForm()
    if form.validate_on_submit():
        orders = connection.query(models.Delivery).filter(func.date(models.Delivery.delivery_date) == cur_date.date(), models.Delivery.status=="assigned", models.Delivery.assigned_driver_id==form.selected_driver.data).all()
        return render_template('/manager/assigned_orders.html', form=form, orders=orders, form1=form1)

    if form1.validate_on_submit():
        line_order_id = request.form.getlist("order_id")

        for i, order_id in enumerate(line_order_id):
            order_to_unassigned = connection.query(models.Delivery).filter(models.Delivery.id==order_id).first()
            if order_to_unassigned.is_received_from_clerk == False:
                order_to_unassigned.status = "unassigned"
                order_to_unassigned.assigned_driver_id = None
                order_to_unassigned.assigned_driver_name = None
                order_to_unassigned.delivery_region = None

        try:
            connection.commit()
        except:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('manager_order.manager_order_assign_region'))
        else:
            return redirect(url_for('manager_order.manager_order_assign_region'))
    return render_template('/manager/assigned_orders.html', form=form, orders=orders, form1=form1)



@manager_order_blueprint.route('/manager/orders/drivers', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_drivers():

    connection = Connection()
    cur_date1 = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    form = DriversSelect()
    
    form.select_drivers.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    orders = []

    if form.validate_on_submit() and form.select_drivers.data != "0":
        user = connection.query(models.User).filter_by(id=form.select_drivers.data).first()
        order_ids = user.current_orders_list

        for i, order_id in enumerate(order_ids):
            order = connection.query(models.Delivery).filter(models.Delivery.id==order_id).first()

            if order:
                orders.append(order)

    return render_template('/manager/driver_current_orders.html', form=form, orders=orders, cur_date1=cur_date1)



@manager_order_blueprint.route('/manager/orders/drivers/histories', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_drivers_histories():

    connection = Connection()
    cur_date1 = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()
    form = DriversHistoriesForm()
    
    form.select_drivers.choices = [(driver.id, f'%s %s'%(driver.lastname, driver.firstname)) for driver in drivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    orders = []

    if form.validate_on_submit() and form.select_drivers.data != "0" and form.date.data is not None:
        orders = connection.query(models.DriverOrderHistory).filter(func.date(models.DriverOrderHistory.created_date) == form.date.data).filter(models.DriverOrderHistory.driver_id==form.select_drivers.data).all()
        return render_template('/manager/drivers_orders_histories.html', form=form, orders=orders, cur_date1=cur_date1)

    return render_template('/manager/drivers_orders_histories.html', form=form, orders=orders, cur_date1=cur_date1)



@manager_order_blueprint.route("/manager/orders/add-detail/<int:order_id>/<int:product_id>/<int:product_quantity>", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_add(order_id, product_id, product_quantity):
    connection = Connection()
    order = connection.query(models.Delivery).get(order_id)

    if order is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    if order.supplier_type == "unstored":
        flash('Өөрчлөх боложгүй', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    if order.is_cancelled:
        flash('Өөрчлөх боложгүй. Хүргэлт цуцалсан байна.', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    is_product = connection.query(models.Product).filter(models.Product.id==int(product_id)).first()

    if is_product:
        is_detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(product_id)).first()

        if is_detail:
            product = connection.query(models.Product).filter(models.Product.id == int(product_id)).first()
            product.inventory.subtract_items(int(product_quantity))
            is_detail.quantity = is_detail.quantity + int(product_quantity)
            order.total_amount = order.total_amount + (int(product_quantity) * product.price)

            if order.is_delivered:
                payment_detail = connection.query(models.PaymentDetail).filter(models.PaymentDetail.delivery_id==order.id).first()
                payment_detail.total_amount = payment_detail.total_amount + (int(is_detail.quantity) * product.price)

            inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==order.id, models.InventoryTransaction.inventory_id==product.inventory.id).first()

            if inventory_transaction:
                inventory_transaction.quantity = inventory_transaction.quantity + product_quantity
            else:
                transaction = models.InventoryTransaction(
                    inventory=product.inventory,
                    quantity=product_quantity,
                    transaction_type='delivery subtraction',
                    delivery_id = order.id)
                product.inventory.transactions.append(transaction)
            
        else:
            order_detail = models.DeliveryDetail()
            order_detail.quantity = int(product_quantity)
            order_detail.product_id = product_id

            product = connection.query(models.Product).filter(models.Product.id == int(product_id)).first()
            product.inventory.subtract_items(int(product_quantity))
            order.total_amount = order.total_amount + (int(product_quantity) * product.price)

            if order.is_delivered:
                payment_detail = connection.query(models.PaymentDetail).filter(models.PaymentDetail.delivery_id==order.id).first()
                payment_detail.total_amount = payment_detail.total_amount + (int(product_quantity) * product.price)

            inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==order.id, models.InventoryTransaction.inventory_id==product.inventory.id).first()

            if inventory_transaction:
                inventory_transaction.quantity = inventory_transaction.quantity + product_quantity
            else:
                transaction = models.InventoryTransaction(
                    inventory=product.inventory,
                    quantity=product_quantity,
                    transaction_type='delivery subtraction',
                    delivery_id = order.id)
                product.inventory.transactions.append(transaction)

            order.delivery_details.append(order_detail)

    try:
        connection.commit()
    except:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))
    else:
        flash('Өөрчлөгдлөө', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))


@manager_order_blueprint.route("/manager/orders/remove-detail/<int:order_detail_id>", methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_orders_remove_detail(order_detail_id):
    connection = Connection()
    detail = connection.query(models.DeliveryDetail).get(order_detail_id)

    if detail is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    order = connection.query(models.Delivery).get(detail.delivery_id)

    if order.supplier_type == "unstored":
        flash('Өөрчлөх боложгүй', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    if order.is_cancelled:
        flash('Өөрчлөх боложгүй. Хүргэлт цуцалсан байна.', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    if order.status == "unassigned":

        if order.is_postphoned:
            is_returned = connection.query(models.DriverReturn.is_returned).filter(models.DriverReturn.delivery_id==order.id).scalar()
            
            if is_returned is False:
                driver_product_return = models.DriverProductReturn()
                driver_product_return.driver_id = order.postphoned_driver_id
                driver_product_return.delivery_id = order.id
                driver_product_return.product_id = detail.product_id
                driver_product_return.driver_comment = "Менежер хассан байна"
                driver_product_return.product_quantity = detail.quantity
                connection.add(driver_product_return)

                product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()

                order.total_amount = order.total_amount - (int(detail.quantity) * product.price)
                order.delivery_details.remove(detail)

            else:
                product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()
                product.inventory.add_items(int(detail.quantity), current_user.id)

                inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==detail.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
                inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

                order.total_amount = order.total_amount - (int(detail.quantity) * product.price)
                order.delivery_details.remove(detail)
        else:
            product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()
            product.inventory.add_items(int(detail.quantity), current_user.id)

            inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==detail.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
            inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

            order.total_amount = order.total_amount - (int(detail.quantity) * product.price)
            order.delivery_details.remove(detail)
        
    elif order.status == "assigned":

        if order.is_received_from_clerk == True:
            product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()

            order.total_amount = order.total_amount - (int(detail.quantity) * product.price)

            driver_product_return = models.DriverProductReturn()
            driver_product_return.driver_id = order.assigned_driver_id
            driver_product_return.delivery_id = order.id
            driver_product_return.product_id = detail.product_id
            driver_product_return.driver_comment = "Менежер хассан байна"
            driver_product_return.product_quantity = detail.quantity
            connection.add(driver_product_return)

            order.delivery_details.remove(detail)

        elif order.is_received_from_clerk == False:
            product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()
            product.inventory.add_items(int(detail.quantity), current_user.id)

            inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==detail.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
            inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

            order.total_amount = order.total_amount - (int(detail.quantity) * product.price)

            order.delivery_details.remove(detail)

    elif order.status == "completed":

        if order.is_received_from_clerk == True:
            product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()

            order.total_amount = order.total_amount - (int(detail.quantity) * product.price)

            payment_detail = connection.query(models.PaymentDetail).filter(models.PaymentDetail.delivery_id==order.id).first()
            payment_detail.total_amount = payment_detail.total_amount - (int(detail.quantity) * product.price)

            driver_product_return = models.DriverProductReturn()
            driver_product_return.driver_id = order.assigned_driver_id
            driver_product_return.delivery_id = order.id
            driver_product_return.product_id = detail.product_id
            driver_product_return.driver_comment = "Менежер хассан байна"
            driver_product_return.product_quantity = detail.quantity
            connection.add(driver_product_return)

            order.delivery_details.remove(detail)

        elif order.is_received_from_clerk == False:
            product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()
            product.inventory.add_items(int(detail.quantity), current_user.id)

            inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==detail.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
            inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

            order.total_amount = order.total_amount - (int(detail.quantity) * product.price)

            payment_detail = connection.query(models.PaymentDetail).filter(models.PaymentDetail.delivery_id==order.id).first()
            payment_detail.total_amount = payment_detail.total_amount - (int(detail.quantity) * product.price)

            order.delivery_details.remove(detail)

    else:
        flash('Өөрчлөх боложгүй', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))

    try:
        connection.commit()
    except Exception as e:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))
    else:
        flash('Бараа хасагдлаа!', 'info')
        return redirect(url_for('manager_order.manager_order_detail', order_id=order.id))