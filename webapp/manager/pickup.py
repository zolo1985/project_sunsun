from flask import (Blueprint, render_template, flash, request, redirect, url_for)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from webapp.manager.forms import DriversDateSelect, FilterDateForm
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz


manager_pickup_blueprint = Blueprint('manager_pickup', __name__)


@manager_pickup_blueprint.route('/manager/pickups', methods=['GET'])
@login_required
@has_role('manager')
def manager_pickups():
    connection = Connection()
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.is_cancelled==False, models.PickupTask.is_completed==False).order_by(models.PickupTask.is_completed.desc()).all()
    return render_template('/manager/pickups.html', pickups=pickups)


@manager_pickup_blueprint.route('/manager/pickups/history', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_pickups_history():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    pickups = connection.query(models.PickupTask).filter(func.date(models.PickupTask.created_date) == cur_date).order_by(models.PickupTask.created_date.desc()).all()

    form = FilterDateForm()

    if form.validate_on_submit() and form.date.data is not None:
        pickups = connection.query(models.PickupTask).filter(func.date(models.PickupTask.created_date) == form.date.data).order_by(models.PickupTask.created_date.desc()).all()
        return render_template('/manager/pickup_histories.html', pickups=pickups, form=form)

    return render_template('/manager/pickup_histories.html', pickups=pickups, form=form)


@manager_pickup_blueprint.route('/manager/pickups/<int:pickup_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_pickup(pickup_id):
    connection = Connection()
    pickup = connection.query(models.PickupTask).get(pickup_id)

    if pickup is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        return redirect(url_for('manager_pickup.manager_pickups'))

    form = DriversDateSelect()
    receivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name == "driver")).filter_by(is_authorized = True).all()
    form.select_drivers.choices = [(receiver.id, f'{receiver.lastname[0].capitalize()}. {receiver.firstname}') for receiver in receivers]
    form.select_drivers.choices.insert(0,(0,'Жолооч сонгох'))
    days = ["Өнөөдөр","Маргааш"]
    form.select_day.choices = [day for day in days]

    if form.validate_on_submit():
        try:
            driver = connection.query(models.User).get(int(form.select_drivers.data))
            
            if form.select_day.data == "Өнөөдөр":
                pickup.status = "enroute"
                pickup.assigned_driver_id = driver.id
                pickup.assigned_manager_id = current_user.id
                pickup.is_driver_assigned = True
                pickup.pickup_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()

            elif form.select_day.data == "Маргааш":
                pickup.status = "enroute"
                pickup.assigned_driver_id = driver.id
                pickup.assigned_manager_id = current_user.id
                pickup.is_driver_assigned = True
                pickup.pickup_date = (datetime.now(pytz.timezone("Asia/Ulaanbaatar")) + + timedelta(hours=+24)).date()
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа.', 'danger')
            connection.rollback()
            return redirect(url_for('manager_pickup.manager_pickups'))
        else:
            flash('Жолооч сонгодлоо', 'success')
            return redirect(url_for('manager_pickup.manager_pickups'))

    return render_template('/manager/pickup.html', pickup=pickup, form=form)