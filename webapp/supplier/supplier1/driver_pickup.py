from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import InventoryPickupAddForm
from datetime import datetime
import pytz


supplier1_driver_pickup_blueprint = Blueprint('supplier1_driver_pickup', __name__)


@supplier1_driver_pickup_blueprint.route('/supplier1/inventories/pickup-task/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickup_add():
    connection = Connection()
    form = InventoryPickupAddForm()
    user_products = connection.query(models.Product).filter(models.Product.supplier_id==current_user.id, models.Product.is_active==True).all()
    form.product.choices = [(product.id, f'%s (хэмжээ: %s, өнгө: %s, төрөл: %s, үнэ: %s₮)'%(product.name, "хэмжээгүй" if product.color is None else product.color, "өнгөгүй" if product.size is None else product.size, "төрөлгүй" if product.type is None else product.type, product.price)) for product in user_products]
    
    if form.validate_on_submit():
        line_quantity = request.form.getlist("quantity")
        line_product = request.form.getlist("product")

        pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).filter(models.PickupTask.is_ready==True).filter(models.PickupTask.is_completed==False).first()

        if pickup_task:
            for i, quantity in enumerate(line_quantity):
                pickup_task_detail = models.PickupTaskDetail()
                pickup_task_detail.quantity = quantity
                pickup_task_detail.product_id = line_product[i]

                pickup_task.pickup_task_details.append(pickup_task_detail)
        else:
            pickup_task = models.PickupTask()
            pickup_task.status = "waiting"
            pickup_task.is_ready = True
            current_user.pickup_tasks.append(pickup_task)

            for i, quantity in enumerate(line_quantity):
                pickup_task_detail = models.PickupTaskDetail()
                pickup_task_detail.quantity = quantity
                pickup_task_detail.product_id = int(line_product[i])
                pickup_task.pickup_task_details.append(pickup_task_detail)

        try:
            connection.commit()
        except Exception as e:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier1_inventory.supplier1_inventory_add'))
        else:
            flash('Хүсэлт үүслээ. Жолооч хувиарлагдахаар очиж авна. Баярлалаа', 'success')
            return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    return render_template('/supplier/supplier1/inventory_add_pickup.html', form=form)


@supplier1_driver_pickup_blueprint.route('/supplier1/inventories/pickup-task/cancel/<int:pickup_task_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickup_cancel(pickup_task_id):
    connection = Connection()
    pickup_task = connection.query(models.PickupTask).get(pickup_task_id)

    if pickup_task is None:
        flash('Хүргэлт олдсонгүй!', 'danger')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    if pickup_task.is_cancelled or pickup_task.is_completed=="completed":
        if pickup_task.is_completed:
            flash('Хүргэгдсэн байна. Цуцлах боломжгүй', 'danger')
        elif pickup_task.is_cancelled:
            flash('Цуцлагдсан байна. Цуцлах боломжгүй', 'danger')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    if current_user.id != pickup_task.supplier_id:
        abort(403)

    try:
        pickup_task_to_update = connection.query(models.PickupTask).get(pickup_task_id)
        pickup_task_to_update.status = "cancelled"
        pickup_task_to_update.is_ready = False
        pickup_task_to_update.is_cancelled = True
        connection.commit()
    except Exception:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))
    else:
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))