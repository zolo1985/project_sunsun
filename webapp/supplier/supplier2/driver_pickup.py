from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier2.forms import DateSelectForm
from datetime import datetime
from webapp.utils import is_time_between
from datetime import datetime, time, timedelta
from sqlalchemy import func
import pytz


supplier2_driver_pickup_blueprint = Blueprint('supplier2_driver_pickup', __name__)


@supplier2_driver_pickup_blueprint.route('/supplier2/driver-pickups', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_driver_pickups():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    form = DateSelectForm()
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id).order_by(models.PickupTask.created_date.desc()).limit(20)
    
    if form.validate_on_submit():
        pickups = connection.query(models.PickupTask).filter(models.PickupTask.supplier_id==current_user.id, func.date(models.PickupTask.created_date) == form.date.data).order_by(models.PickupTask.created_date.desc()).limit(20)
        return render_template('/supplier/supplier2/pickups.html', pickups=pickups, cur_date=cur_date, form=form)

    return render_template('/supplier/supplier2/pickups.html', pickups=pickups, cur_date=cur_date, form=form)


@supplier2_driver_pickup_blueprint.route('/supplier2/driver-pickups/confirmation/<int:pickup_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('supplier2')
def supplier2_driver_pickups_confirmation(pickup_task_id):
    connection = Connection()
    try:
        pickup_task = connection.query(models.PickupTask).get(pickup_task_id)

        if pickup_task.status == "enroute":
            for pickup_task_detail in pickup_task.pickup_task_details:

                new_delivery = models.Delivery()
                new_delivery.status = "unassigned"
                new_delivery.destination_type = pickup_task_detail.destination_type
                new_delivery.supplier_type = "unstored"
                new_delivery.delivery_attempts = 0
                new_delivery.total_amount = pickup_task_detail.total_amount
                new_delivery.instruction = pickup_task_detail.comment
                #do not remove this modified date
                new_delivery.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                new_delivery.delivery_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                    
                delivery_detail = models.DeliveryDetail()
                delivery_detail.quantity = 1

                delivery_address = models.Address()
                delivery_address.phone = pickup_task_detail.phone
                delivery_address.phone_more = pickup_task_detail.phone_more
                delivery_address.district = pickup_task_detail.district
                delivery_address.khoroo = pickup_task_detail.khoroo
                delivery_address.aimag = pickup_task_detail.aimag
                delivery_address.address = pickup_task_detail.address
                
                new_delivery.delivery_details.append(delivery_detail)
                new_delivery.addresses = delivery_address
                current_user.deliveries.append(new_delivery)
                connection.flush()

                new_unstored_inventory = models.UnstoredInventory()
                new_unstored_inventory.clerk_received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                new_unstored_inventory.received_clerk_id = current_user.id
                new_unstored_inventory.supplier_id = pickup_task.supplier_id
                new_unstored_inventory.delivery_id = new_delivery.id
                connection.add(new_unstored_inventory)

            pickup_task.status = "pickedup"
            pickup_task.is_ready = False
            pickup_task.is_driver_received = True
            connection.commit()

    except Exception as e:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))
    else:
        flash('Жолооч хүлээж авлаа. Хүргэлтүүд үүслээ', 'success')
        return redirect(url_for('supplier2_driver_pickup.supplier2_driver_pickups'))