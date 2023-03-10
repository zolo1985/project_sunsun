from flask import (Blueprint, render_template, redirect, url_for, flash, jsonify, request)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp.clerk.forms import FilterDateForm
from webapp import models
from datetime import datetime
from sqlalchemy import func
import pytz


clerk_return_task_blueprint = Blueprint('clerk_return_task', __name__)


@clerk_return_task_blueprint.route('/clerk/return-task/<int:unstored_inventory_id>', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_return_task_add(unstored_inventory_id):
    connection = Connection()

    unstored_inventory = connection.query(models.UnstoredInventory).filter(models.UnstoredInventory.id==unstored_inventory_id, models.UnstoredInventory.is_returned_to_supplier==False).first()

    if not unstored_inventory:
        flash('Олдсонгүй','danger')
        return redirect(url_for('clerk_inventory.clerk_unstored_inventories'))

    if unstored_inventory.is_returned_to_supplier is True:
        flash('Буцаагдсан байна! Дахин буцаагдах боломжгүй','info')
        return redirect(url_for('clerk_inventory.clerk_unstored_inventories'))

    try:
        is_return_task = connection.query(models.ReturnTask).filter(models.ReturnTask.status=="waiting", models.ReturnTask.is_ready==True, models.ReturnTask.supplier_id==unstored_inventory.supplier_id).first()

        if is_return_task:
            new_return_task_detail = models.ReturnTaskDetail()
            new_return_task_detail.quantity = 1
            new_return_task_detail.phone = unstored_inventory.delivery.addresses.phone

            is_return_task.return_task_details.append(new_return_task_detail)
        else:
            new_return_task = models.ReturnTask()
            new_return_task.is_ready = True
            new_return_task.status = "waiting"
            new_return_task.supplier_id = unstored_inventory.supplier_id

            new_return_task_detail = models.ReturnTaskDetail()
            new_return_task_detail.quantity = 1
            new_return_task_detail.phone = unstored_inventory.delivery.addresses.phone

            new_return_task.return_task_details.append(new_return_task_detail)
            connection.add(new_return_task)

        unstored_inventory.is_returned_to_supplier = True

        connection.commit()
    except Exception as ex:
        flash("Алдаа гарлаа!", 'danger')
        connection.rollback()
        return redirect(url_for('clerk_inventory.clerk_unstored_inventories'))
    else:
        flash("Буцаалт үүслээ. Менежер жолооч хувиарлахад бэлэн боллоо.", 'success')
        return redirect(url_for('clerk_inventory.clerk_unstored_inventories'))