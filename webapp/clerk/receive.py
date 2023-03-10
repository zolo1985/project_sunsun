from flask import (Blueprint, flash, redirect, render_template, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from datetime import datetime
from webapp.clerk.forms import ReceiveInventoryForm
from sqlalchemy import func, desc
import pytz

clerk_receive_blueprint = Blueprint('clerk_receive', __name__)

@clerk_receive_blueprint.route('/clerk/pickup-receive', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_receive_pickup_inventories():
    connection = Connection()
    pickups = connection.query(models.PickupTask).order_by(models.PickupTask.created_date.desc()).all()
    return render_template('/clerk/receive_pickup_inventories.html', pickups=pickups)


@clerk_receive_blueprint.route('/clerk/pickup-receive/<int:pickup_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_accept_pickup_inventories(pickup_task_id):
    connection = Connection()
    pickup_task = connection.query(models.PickupTask).filter(models.PickupTask.is_completed==False, models.PickupTask.is_cancelled==False, models.PickupTask.id==pickup_task_id).first()

    if pickup_task is None:
        flash('Олдонгүй', 'danger')
        return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    if pickup_task.is_completed is True or pickup_task.is_cancelled is True:
        flash('Ажил дууссан байна', 'info')
        return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    if pickup_task.supplier.has_role('supplier1'):
        try:
            for detail in pickup_task.pickup_task_details:
                product = connection.query(models.Product).get(detail.product_id)
                product.inventory.add_items(int(detail.quantity), int(current_user.id))
                
                transaction = models.InventoryTransaction(inventory=product.inventory, quantity=detail.quantity, transaction_type='inventory addition')
                product.inventory.transactions.append(transaction)

            driver_task_history = models.DriverOrderHistory()
            driver_task_history.supplier_name = pickup_task.supplier.company_name
            driver_task_history.type = "pickup"
            driver_task_history.status = "completed"
            driver_task_history.pickup_task_id = pickup_task.id
            driver_task_history.driver_id = pickup_task.assigned_driver_id
            connection.add(driver_task_history)

            pickup_task.status = "completed"
            pickup_task.is_completed = True
            
            pickup_task.received_clerk_id = current_user.id
            pickup_task.clerk_received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))
        else:
            flash("Бараа хүлээж авлаа.", 'success')
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    elif pickup_task.supplier.has_role('supplier2'):
        try:
            driver_task_history = models.DriverOrderHistory()
            driver_task_history.supplier_name = pickup_task.supplier.company_name
            driver_task_history.type = "pickup"
            driver_task_history.status = "completed"
            driver_task_history.pickup_task_id = pickup_task.id
            driver_task_history.driver_id = pickup_task.assigned_driver_id
            connection.add(driver_task_history)

            pickup_task.status = "completed"
            pickup_task.is_completed = True
            
            pickup_task.received_clerk_id = current_user.id
            pickup_task.clerk_received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))
        else:
            flash("Бараа хүлээж авлаа.", 'success')
            return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))


@clerk_receive_blueprint.route('/clerk/dropoff-receive')
@login_required
@has_role('clerk')
def clerk_receive_dropoff_inventories():
    connection = Connection()
    supplier_dropoffs = connection.query(models.SupplierDropoffTask).order_by(models.SupplierDropoffTask.created_date.desc()).all()
    return render_template('/clerk/receive_dropoff_inventories.html', supplier_dropoffs=supplier_dropoffs)


@clerk_receive_blueprint.route('/clerk/dropoff-receive/<int:supplier_dropoff_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_accept_dropoff_inventories(supplier_dropoff_task_id):
    connection = Connection()
    supplier_dropoff_task = connection.query(models.SupplierDropoffTask).filter(models.SupplierDropoffTask.status=="waiting", models.SupplierDropoffTask.id==supplier_dropoff_task_id).first()

    if supplier_dropoff_task is None:
        flash('Олдонгүй', 'danger')
        return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    if supplier_dropoff_task.is_completed is True or supplier_dropoff_task.is_cancelled is True:
        flash('Ажил дууссан байна', 'info')
        return redirect(url_for('clerk_receive.clerk_receive_pickup_inventories'))

    supplier_dropoff_task.status = "completed"
    supplier_dropoff_task.is_completed = True
    supplier_dropoff_task.is_ready = False
    
    supplier_dropoff_task.received_clerk_id = current_user.id
    supplier_dropoff_task.clerk_received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    if supplier_dropoff_task.supplier.has_role('supplier1'):
        try:
            for detail in supplier_dropoff_task.supplier_dropoff_task_details:
                product = connection.query(models.Product).get(detail.product_id)
                product.inventory.add_dropoff_items(int(detail.quantity), int(current_user.id))
                
                transaction = models.InventoryTransaction(inventory=product.inventory, quantity=detail.quantity, transaction_type='inventory addition')
                product.inventory.transactions.append(transaction)

            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
        else:
            flash("Бараа хүлээж авлаа.", 'success')
            return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))

    elif supplier_dropoff_task.supplier.has_role('supplier2'):
        # for detail in pickup_task.pickup_task_details:
        #     inventory_to_update = connection.query(models.Inventory).get(detail.inventory_id)
            # inventory_to_update.clerk_name = f'%s %s'%(current_user.lastname, current_user.firstname)
            # inventory_to_update.clerk_id = current_user.id
            # inventory_to_update.clerk_accepted_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            # inventory_to_update.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception as ex:
            flash("Алдаа гарлаа!", 'danger')
            connection.rollback()
            return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
        else:
            flash("Бараа хүлээж авлаа.", 'success')
            return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))


# @clerk_receive_blueprint.route('/clerk/dropoff-receive/cancel/<int:inventory_id>', methods=['GET','POST'])
# @login_required
# @has_role('clerk')
# def clerk_cancel_dropoff_inventories(inventory_id):
#     connection = Connection()
#     inventory = connection.query(models.Inventory).filter(models.Inventory.id==inventory_id, models.Inventory.status==False).first()

#     if inventory is None:
#         flash('Олдонгүй')
#         return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))

#     if inventory.received_clerk_id is not None and inventory.received_clerk_id != current_user.id:
#         flash("Ачааг зөвхөн харилцагч хүлээгэж өгсөн нярав авах, өөрчлөх эрхтэй!", 'warning')
#         return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
#     else:
#         try:
#             inventory_to_update = connection.query(models.Inventory).filter(models.Inventory.id==inventory_id).first()


#             connection.commit()
#         except Exception as ex:
#             flash(f'{ex}', 'danger')
#             flash("Алдаа гарлаа!", 'danger')
#             connection.rollback()
#             return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
#         else:
#             flash("Цуцаллаа.", 'success')
#             return redirect(url_for('clerk_receive.clerk_receive_dropoff_inventories'))
    