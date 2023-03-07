from flask import (Blueprint, flash, redirect, render_template,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from datetime import datetime
import pytz


supplier2_return_task_blueprint = Blueprint('supplier2_return_task', __name__)


@supplier2_return_task_blueprint.route('/supplier2/return-tasks', methods=['GET'])
@login_required
@has_role('supplier2')
def supplier2_return_tasks():
    connection = Connection()
    return_tasks = connection.query(models.ReturnTask).filter(models.ReturnTask.supplier_id==current_user.id).limit(10)
    return render_template('/supplier/supplier2/return_tasks.html', return_tasks=return_tasks)


@supplier2_return_task_blueprint.route('/supplier2/return-tasks/receive/<int:return_task_id>', methods=['GET'])
@login_required
@has_role('supplier2')
def supplier2_return_task_receive(return_task_id):
    connection = Connection()
    return_task = connection.query(models.ReturnTask).get(return_task_id)

    if return_task is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('supplier2_return_task.supplier2_return_tasks'))

    if return_task.supplier_id != current_user.id:
        abort(403)

    if return_task.is_completed==True or return_task.is_cancelled==True:
        flash('Буцааж авсан эсвэл цуцалсан байна', 'info')
        return redirect(url_for('supplier2_return_task.supplier2_return_tasks'))

    if return_task.is_completed==False and return_task.is_cancelled==False:

        try:
            return_task.is_completed = True
            return_task.status = 'completed'
            return_task.supplier_received_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            driver_task_history = models.DriverOrderHistory()
            driver_task_history.supplier_name = return_task.supplier.company_name
            driver_task_history.type = "return task"
            driver_task_history.status = "completed"
            driver_task_history.return_task_id = return_task.id
            driver_task_history.driver_id = return_task.assigned_driver_id
            connection.add(driver_task_history)
            connection.commit()
        except:
            connection.rollback()
        else:
            flash('Хүлээж авлаа', 'success')
            return redirect(url_for('supplier2_return_task.supplier2_return_tasks'))
            
    else:
        flash('Хүлээж авсан байна', 'info')
        return redirect(url_for('supplier2_return_task.supplier2_return_tasks'))
