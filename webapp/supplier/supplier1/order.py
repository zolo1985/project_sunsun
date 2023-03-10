from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, jsonify, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import OrderAddForm, FiltersForm
from datetime import datetime, time, timedelta
from sqlalchemy import func, or_
from webapp.utils import is_time_between
import pytz


supplier1_order_blueprint = Blueprint('supplier1_order', __name__)


initial_districts = ['Багануур', 'Багахангай', 'Баянгол', 'Баянзүрх', 'Налайх', 'Хан-Уул', 'Сүхбаатар', 'Сонгинохайрхан', 'Чингэлтэй']
initial_aimags = ['Архангай','Баян-Өлгий','Баянхонгор','Булган','Говь-Алтай','Говьсүмбэр','Дархан-Уул','Дорноговь','Дорнод','Дундговь','Завхан','Орхон','Өвөрхангай','Өмнөговь','Сүхбаатар','Сэлэнгэ','Төв','Увс','Ховд','Хөвсгөл','Хэнтий']


@supplier1_order_blueprint.route('/supplier1/orders', methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_orders():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = FiltersForm()
    orders = []
    orders = connection.query(models.Delivery).filter(models.Delivery.user_id == current_user.id, or_(func.date(models.Delivery.delivery_date) == cur_date.date(), func.date(models.Delivery.created_date) == cur_date.date(), (func.date(models.Delivery.postphoned_date) == cur_date.date()) & (models.Delivery.is_postphoned == True))).order_by(models.Delivery.created_date).all()

    if form.validate_on_submit() and form.date.data is not None:
        orders = connection.query(models.Delivery).filter(models.Delivery.user_id == current_user.id, or_(func.date(models.Delivery.delivery_date) == form.date.data, func.date(models.Delivery.created_date) == form.date.data, (func.date(models.Delivery.postphoned_date) == form.date.data) & (models.Delivery.is_postphoned == True))).all()
        return render_template('/supplier/supplier1/orders.html', orders=orders, cur_date=cur_date, form=form)

    return render_template('/supplier/supplier1/orders.html', orders=orders, cur_date=cur_date, form=form)


@supplier1_order_blueprint.route('/supplier1/orders/add', methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_order_add():

    connection = Connection()

    form = OrderAddForm()

    form.district.choices = [(district) for district in initial_districts]
    form.district.choices.insert(0,'Дүүрэг сонгох')
    form.khoroo.choices = [(f'%s'%(khoroo+1)) for khoroo in range(50)]
    form.khoroo.choices.insert(0,'Хороо сонгох')
    form.aimag.choices = [(aimag) for aimag in initial_aimags]
    form.aimag.choices.insert(0,'Аймаг сонгох')

    if form.validate_on_submit():
        line_products = request.form.getlist("product")
        line_quantities = request.form.getlist("quantity")

        if form.order_type.data == "0":
            try:
                order = models.Delivery()
                order.status = "unassigned"
                order.destination_type = "local"
                order.supplier_type = "stored"
                order.delivery_attempts = 0
                order.total_amount = abs(form.total_amount.data)

                if is_time_between(time(6,30), time(10,30)):
                    order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    #dont remove this modified date
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                else:
                    next_day = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + timedelta(hours=+24)
                    next_day_mid_night = next_day.replace(hour=0, minute=5)
                    order.delivery_date = next_day_mid_night
                    order.modified_date = next_day_mid_night

                current_user.deliveries.append(order)
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
                return redirect(url_for('supplier1_order.supplier1_orders'))
            else:
                if is_time_between(time(6,30), time(10,30)):
                    flash('Хүргэлт нэмэгдлээ.', 'success')
                else:
                    flash('Маргаашийн хүргэлтэнд нэмэгдлээ.', 'success')
                return redirect(url_for('supplier1_order.supplier1_order_add', destination='local'))

        elif form.order_type.data == "1":
            try:
                order = models.Delivery()
                order.status = "unassigned"
                order.destination_type = "long"
                order.supplier_type = "stored"
                order.delivery_attempts = 0
                order.total_amount = abs(form.total_amount.data)

                if is_time_between(time(6,30), time(10,30)):
                    order.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    #dont remove this modified date
                    order.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                else:
                    next_day = datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + timedelta(hours=+24)
                    next_day_mid_night = next_day.replace(hour=0, minute=5)
                    order.delivery_date = next_day_mid_night

                current_user.deliveries.append(order)
                connection.flush()
                
                address = models.Address()
                address.phone = form.phone.data
                address.phone_more = form.phone_more.data
                address.aimag = form.aimag.data
                address.address = form.address.data
                
                order.addresses = address
                
                for i, prod in enumerate(line_products):
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
                return redirect(url_for('supplier1_order.supplier1_orders'))
            else:
                if is_time_between(time(6,30), time(10,30)):
                    flash('Хүргэлт нэмэгдлээ.', 'success')
                else:
                    flash('Маргаашийн хүргэлтэнд нэмэгдлээ.', 'success')
                return redirect(url_for('supplier1_order.supplier1_order_add', destination='long'))

    return render_template('/supplier/supplier1/order_add.html', form=form)


@supplier1_order_blueprint.route("/supplier1/orders/search/products", methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_search_products():
    query = request.form.get("term")
    connection = Connection()
    search = "%{}%".format(query)
    products = connection.query(models.Product).filter(models.Product.supplier_id==current_user.id, models.Product.name.like(search)).all()
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


@supplier1_order_blueprint.route('/supplier1/orders/cancel/<int:order_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_order_cancel(order_id):
    connection = Connection()
    order_to_cancel = connection.query(models.Delivery).filter(models.Delivery.id==order_id).first()

    if order_to_cancel is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier1_order.supplier1_orders'))

    if order_to_cancel.user_id != current_user.id:
        abort(403)

    if order_to_cancel.status != "unassigned":
        flash('Хүргэлт цуцлах боломжгүй байна! Менежертэй холбоо барина уу!', 'danger')
        return redirect(url_for('supplier1_order.supplier1_orders'))
    else:
        if order_to_cancel.status == "unassigned" and order_to_cancel.is_postphoned is False and order_to_cancel.is_received_from_clerk is False:
            order_to_cancel.status = "cancelled"
            order_to_cancel.is_cancelled = True
            order_to_cancel.is_delivered = False
            order_to_cancel.driver_comment = "Харилцагч цуцалсан."
            order_to_cancel.show_comment = True
            order_to_cancel.show_status = True

            for detail in order_to_cancel.delivery_details:
                product = connection.query(models.Product).filter(models.Product.id == detail.product_id).first()
                product.inventory.add_items(detail.quantity, current_user.id)

                inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.inventory_id==product.inventory.id, models.InventoryTransaction.delivery_id==order_to_cancel.id).first()
                inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

            try:
                connection.commit()
            except Exception as ex:
                connection.rollback()
                return redirect(url_for('supplier1_order.supplier1_orders'))
            else:
                flash('Хүргэлт цуцлагдлаа', 'success')
                return redirect(url_for('supplier1_order.supplier1_orders'))

        else:
            flash('Хүргэлт цуцлах боломжгүй байна! Менежертэй холбоо барина уу!', 'info')
            return redirect(url_for('supplier1_order.supplier1_orders'))
