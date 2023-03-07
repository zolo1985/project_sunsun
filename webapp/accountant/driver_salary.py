from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp.accountant.forms import DateSelect
from webapp import models
from datetime import datetime, timedelta
import calendar
import pytz
from dateutil.rrule import DAILY,rrule

accountant_driver_salary_blueprint = Blueprint('accountant_driver_salary', __name__)

@accountant_driver_salary_blueprint.route('/accountant/driver-salary', methods=['GET','POST'])
@login_required
@has_role('accountant')
def accountant_driver_salary():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    form = DateSelect()

    if form.validate_on_submit():
        selected_date = form.select_date.data
        if selected_date.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(selected_date.year, selected_date.month)[1]
    else:
        selected_date = current_date
        if current_date.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(current_date.year, current_date.month)[1]

    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
    drivers_datas = []

    for driver in drivers:
        data_format = [f"{driver.lastname[0].capitalize()}. {driver.firstname}", driver.id]
        days_list = [
            (i.day,
            connection.execute("SELECT COUNT(delivery.id) as total_delivery_count FROM sunsundatabase1.user as driver join sunsundatabase1.delivery as delivery on driver.id=delivery.assigned_driver_id where (date(delivery.delivered_date)=:date0) and driver.id=:driver_id and delivery.is_delivered=true group by driver.id", {"date0":i.date(), "driver_id": driver.id},).scalar() or 0,
            connection.execute("SELECT COUNT(*) as total FROM sunsundatabase1.pickup_task as pickup WHERE (pickup.clerk_received_date BETWEEN :date1 AND :date2) and pickup.assigned_driver_id=:driver_id and pickup.status='completed';", {"date1": (i - timedelta(days=1)).replace(hour=17, minute=0), "date2": i.replace(hour=17, minute=0), "driver_id": driver.id},).scalar() or 0,
            connection.execute("SELECT COUNT(*) as total FROM sunsundatabase1.return_task as return_task WHERE (return_task.supplier_received_date BETWEEN :date1 AND :date2) and return_task.assigned_driver_id=:driver_id and return_task.is_completed=true;", {"date1": (i - timedelta(days=1)).replace(hour=17, minute=0), "date2": i.replace(hour=17, minute=0), "driver_id": driver.id},).scalar() or 0,)
            for i in rrule(DAILY, dtstart=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{end_day}', '%Y-%m-%d'))]
        days_data = [i.day for i in rrule(DAILY, dtstart=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{end_day}', '%Y-%m-%d'))]
        driver_remaing_balance = connection.execute("SELECT sum(sap.remaining_amount) FROM sunsundatabase1.payment as sap where (DATE(sap.date_of_payment) BETWEEN DATE(:start_date) AND DATE(:end_date)) and sap.driver_id=:driver_id group by sap.driver_id;", {"start_date": datetime.strptime(f'{selected_date.year}-{selected_date.month}-{start_day}', '%Y-%m-%d'), "end_date": datetime.strptime(f'{selected_date.year}-{selected_date.month}-{end_day}', '%Y-%m-%d'), "driver_id": driver.id}).scalar()

        data_format.insert(2, (days_list))
        data_format.insert(3, driver.delivery_rate)
        data_format.insert(4, int(driver_remaing_balance) if driver_remaing_balance is not None else 0)
        drivers_datas.append(data_format)

    return render_template('/accountant/driver_salary.html', current_date=selected_date, datas = drivers_datas, day_list=days_data, form=form)