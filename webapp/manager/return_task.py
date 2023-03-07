from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import DriversDateSelect, FilterDateForm
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz


manager_return_task_blueprint = Blueprint('manager_return_task', __name__)

@manager_return_task_blueprint.route('/manager/return-tasks', methods=['GET'])
@login_required
@has_role('manager')
def manager_return_tasks():
    connection = Connection()
    return_tasks = connection.query(models.ReturnTask).filter(models.ReturnTask.is_cancelled==False, models.ReturnTask.is_completed==False).order_by(models.ReturnTask.is_completed.desc()).all()
    return render_template('/manager/return_tasks.html', return_tasks=return_tasks)


@manager_return_task_blueprint.route('/manager/return-tasks/<int:return_task_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_return_task(return_task_id):
    connection = Connection()
    return_task = connection.query(models.ReturnTask).get(return_task_id)

    if return_task is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('manager_return_task.manager_return_tasks'))

    form = DriversDateSelect()
    receivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "driver")).filter_by(is_authorized = True).all()
    form.select_drivers.choices = [(receiver.id, f'{receiver.lastname[0].capitalize()}. {receiver.firstname}') for receiver in receivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    days = ["Өнөөдөр","Маргааш"]
    form.select_day.choices = [day for day in days]

    if form.validate_on_submit():
        try:
            driver = connection.query(models.User).get(int(form.select_drivers.data))
            return_task.status = "enroute"
            return_task.assigned_driver_id = driver.id
            return_task.assigned_manager_id = current_user.id
            return_task.is_driver_assigned = True
        
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа.', 'danger')
            connection.rollback()
            return redirect(url_for('manager_return_task.manager_return_tasks'))
        else:
            flash('Жолооч сонгодлоо', 'success')
            return redirect(url_for('manager_return_task.manager_return_tasks'))

    return render_template('/manager/return_task.html', return_task=return_task, form=form)


@manager_return_task_blueprint.route('/manager/return_tasks/history', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_return_tasks_history():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    return_tasks = connection.query(models.ReturnTask).filter(func.date(models.ReturnTask.created_date) == cur_date).all()

    form = FilterDateForm()

    if form.validate_on_submit() and form.date.data is not None:
        return_tasks = connection.query(models.ReturnTask).filter(func.date(models.ReturnTask.created_date) == form.date.data).all()
        return render_template('/manager/return_task_histories.html', return_tasks=return_tasks, form=form)

    return render_template('/manager/return_task_histories.html', return_tasks=return_tasks, form=form)