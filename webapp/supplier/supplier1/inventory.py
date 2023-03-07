from flask import (Blueprint, redirect, render_template,
                   url_for, flash, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import ChooseType, DriverPickupForm, FiltersForm
from datetime import datetime
import pytz
import calendar
from dateutil.rrule import DAILY,rrule
from sqlalchemy import func, or_


supplier1_inventory_blueprint = Blueprint('supplier1_inventory', __name__)


@supplier1_inventory_blueprint.route('/supplier1/inventories', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventories():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()

    final_inventories = []
    days_data = []

    form = FiltersForm()

    if current_date.day <= 15:
        start_day = 1
        end_day = 15
    else:
        start_day = 16
        end_day = calendar.monthrange(current_date.year, current_date.month)[1]

    for product in current_user.products:
        data_format = [f"%s (%s, %s, %s)"%(product.name.capitalize(), "өнгөгүй" if product.color is None else product.color, "хэмжээгүй" if product.size is None else product.size, "төрөлгүй" if product.type is None else product.type), int(product.inventory.get_items())]
        days_list = []
        days_data = []
        for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
            day_added = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, models.InventoryTransaction.transaction_type == 'inventory addition', func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
            day_expense = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, or_(models.InventoryTransaction.transaction_type == 'inventory subtraction', models.InventoryTransaction.transaction_type == 'delivery subtraction', models.InventoryTransaction.transaction_type == 'warehouse sale subtraction'), func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
            day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
            days_list.append(day_format)
            days_data.append(i.day)

        data_format.insert(2, (days_list))
        data_format.insert(3, product.price)
        final_inventories.append(data_format)

    if form.date.data is not None and form.validate_on_submit():

        final_inventories = []
        days_data = []

        if form.date.data.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(form.date.data.year, form.date.data.month)[1]

        for product in current_user.products:
            data_format = [f"%s (%s, %s, %s)"%(product.name.capitalize(), "өнгөгүй" if product.color is None else product.color, "хэмжээгүй" if product.size is None else product.size, "төрөлгүй" if product.type is None else product.type), int(product.inventory.get_items())]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
                day_added = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, models.InventoryTransaction.transaction_type == 'inventory addition', func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
                day_expense = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, or_(models.InventoryTransaction.transaction_type == 'inventory subtraction', models.InventoryTransaction.transaction_type == 'delivery subtraction', models.InventoryTransaction.transaction_type == 'warehouse sale subtraction'), func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
                day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            data_format.insert(3, product.price)
            final_inventories.append(data_format)

        return render_template('/supplier/supplier1/inventories.html', form=form, current_date=form.date.data, day_list=days_data, final_inventories=final_inventories)

    return render_template('/supplier/supplier1/inventories.html', form=form, current_date=current_date, day_list=days_data, final_inventories=final_inventories)


@supplier1_inventory_blueprint.route('/supplier1/inventories/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_add():

    form = ChooseType()

    if form.validate_on_submit():
        if form.delivery_type.data == "0":
            return redirect(url_for('supplier1_driver_pickup.supplier1_inventory_pickup_add'))
        elif form.delivery_type.data == "1":
            return redirect(url_for('supplier1_dropoff.supplier1_inventory_dropoff_add'))
        else:
            return render_template('/supplier/supplier1/inventory_add.html', form=form)

    return render_template('/supplier/supplier1/inventory_add.html', form=form)


@supplier1_inventory_blueprint.route('/supplier1/inventories/pickups-and-dropoffs', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickups_and_dropoffs():
    form = DriverPickupForm()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id == current_user.id, func.date(models.PickupTask.created_date) == cur_date.date()).limit(20)
    dropoffs = connection.query(models.SupplierDropoffTask).filter(models.SupplierDropoffTask.supplier_id == current_user.id, func.date(models.SupplierDropoffTask.created_date) == cur_date.date()).limit(20)

    if form.validate_on_submit():
        pickups = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id == current_user.id, func.date(models.PickupTask.created_date) == form.date.data).limit(20)
        dropoffs = connection.query(models.SupplierDropoffTask).filter(models.SupplierDropoffTask.supplier_id == current_user.id, func.date(models.SupplierDropoffTask.created_date) == form.date.data).limit(20)
        return render_template('/supplier/supplier1/pickup_inventories.html', pickups=pickups, form=form, dropoffs=dropoffs)
    return render_template('/supplier/supplier1/pickup_inventories.html', pickups=pickups, form=form, dropoffs=dropoffs)


@supplier1_inventory_blueprint.route('/supplier1/inventories/pickups/confirmation/<int:pickup_task_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_pickups_and_dropoffs_confirmation(pickup_task_id):
    connection = Connection()
    pickup = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id == current_user.id, models.PickupTask.id==pickup_task_id, models.PickupTask.is_ready==True).first()

    if pickup is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    if pickup.supplier_id != current_user.id:
        abort(403)

    if pickup.is_driver_received is True and pickup.is_completed is False:
        flash('Жолооч хүлээж авсан байна', 'info')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    if pickup.is_completed is True or pickup.is_cancelled is True:
        flash('Ажил дууссан байна', 'info')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    try:
        pickup_task_to_update = connection.query(models.PickupTask).get(pickup_task_id)
        pickup_task_to_update.status = "pickedup"
        pickup_task_to_update.is_ready = False
        pickup_task_to_update.is_driver_received = True
        connection.commit()
    except Exception:
        connection.rollback()
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))
    else:
        flash('Жолооч барааг хүлээж авлаа. Нярав хүлээж авсны дараа агуулахын үлдэгдэл өөрчлөгдөж, захиалга үүсгэх боломжтой болохыг анхаарна уу!', 'success')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))


@supplier1_inventory_blueprint.route('/supplier1/inventories/dropoffs/confirmation/<int:dropoff_task_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_inventory_dropoff_confirmation(dropoff_task_id):
    connection = Connection()
    dropoff = connection.query(models.SupplierDropoffTask).filter(models.SupplierDropoffTask.supplier_id == current_user.id, models.SupplierDropoffTask.id==dropoff_task_id, models.SupplierDropoffTask.is_ready==True).first()

    if dropoff is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    if dropoff.supplier_id != current_user.id:
        abort(403)

    if dropoff.is_completed is True or dropoff.is_cancelled is True:
        flash('Ажил дууссан байна', 'info')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))

    try:
        dropoff_task_to_update = connection.query(models.SupplierDropoffTask).get(dropoff_task_id)
        dropoff_task_to_update.status = "pickedup"
        dropoff_task_to_update.is_ready = False
        dropoff_task_to_update.is_driver_received = True
        connection.commit()
    except Exception:
        connection.rollback()
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))
    else:
        flash('Жолооч барааг хүлээж авлаа. Нярав хүлээж авсны дараа агуулахын үлдэгдэл өөрчлөгдөж, захиалга үүсгэх боломжтой болохыг анхаарна уу!', 'success')
        return redirect(url_for('supplier1_inventory.supplier1_inventory_pickups_and_dropoffs'))


    

    
