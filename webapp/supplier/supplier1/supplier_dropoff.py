from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import InventoryAddForm


supplier1_dropoff_blueprint = Blueprint('supplier1_dropoff', __name__)


@supplier1_dropoff_blueprint.route('/supplier1/inventories/dropoff/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_dropoff_add():
    connection = Connection()
    form = InventoryAddForm()
    user_products = connection.query(models.Product).filter(models.Product.supplier_id==current_user.id, models.Product.is_active==True).all()
    form.product.choices = [(product.id, f'%s (хэмжээ: %s, өнгө: %s, төрөл: %s, үнэ: %s₮)'%(product.name, "хэмжээгүй" if product.color is None else product.color, "өнгөгүй" if product.size is None else product.size, "төрөлгүй" if product.type is None else product.type, product.price)) for product in user_products]
    
    if form.validate_on_submit():
        line_quantity = request.form.getlist("quantity")
        line_product = request.form.getlist("product")

        try:
            supplier_dropoff_task = models.SupplierDropoffTask()
            supplier_dropoff_task.status = "waiting"
            supplier_dropoff_task.is_ready = True
            current_user.supplier_dropoff_tasks.append(supplier_dropoff_task)

            for i, quantity in enumerate(line_quantity):
                supplier_dropff_task_detail = models.SupplierDropoffTaskDetail()
                supplier_dropff_task_detail.quantity = quantity
                supplier_dropff_task_detail.product_id = int(line_product[i])
                supplier_dropoff_task.supplier_dropoff_task_details.append(supplier_dropff_task_detail)

            connection.commit()
        
        except Exception as e:
            flash(f'{e}', 'danger')
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))
        else:
            flash('Бараа амжилттай хүлээлгэж өглөө. Хэрвээ жолоочид өгсөн бол нярав хүлээлгэж өгтөл хүлээгдэхийг анхаарна уу! Баярлалаа', 'success')
            return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    return render_template('/supplier/supplier1/inventory_add_dropoff.html', form=form)


@supplier1_dropoff_blueprint.route('/supplier1/inventories/dropoff/cancel/<int:dropoff_task_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_dropoff_cancel(dropoff_task_id):
    connection = Connection()
    dropoff_task = connection.query(models.SupplierDropoffTask).get(dropoff_task_id)

    if dropoff_task is None:
        flash('Олдсонгүй!', 'danger')
        return redirect(url_for('supplier1_inventory_pickups_and_dropoffs'))

    if dropoff_task.is_cancelled or dropoff_task.is_completed=="completed":
        if dropoff_task.is_completed:
            flash('Хүрлээлгэж өгсөн байна. Цуцлах боломжгүй', 'danger')
        elif dropoff_task.is_cancelled:
            flash('Цуцлагдсан байна. Цуцлах боломжгүй', 'danger')
        return redirect(url_for('supplier1_inventory_pickups_and_dropoffs'))

    if current_user.id != dropoff_task.supplier_id:
        abort(403)

    try:
        dropoff_task_to_update = connection.query(models.SupplierDropoffTask).get(dropoff_task_id)
        dropoff_task_to_update.status = "cancelled"
        dropoff_task_to_update.is_ready = False
        dropoff_task_to_update.is_cancelled = True
        connection.commit()
    except Exception:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))
    else:
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))