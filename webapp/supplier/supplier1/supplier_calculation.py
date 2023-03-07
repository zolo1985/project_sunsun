from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp.supplier.supplier1.forms import DateSelect
from webapp import models
from sqlalchemy import or_
from datetime import datetime, timedelta
from dateutil.rrule import DAILY,rrule
import calendar
import pytz


supplier1_calculation_blueprint = Blueprint('supplier1_calculation', __name__)


@supplier1_calculation_blueprint.route('/supplier1/calculation/two-weeks', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_calculation_two_week():

    connection = Connection()

    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    suppliers_datas = []

    if current_date.day <= 15:
        start_day = 1
        end_day = 15
    else:
        start_day = 16
        end_day = calendar.monthrange(current_date.year, current_date.month)[1]

    supplier_format = [current_user.company_name, current_user.id, current_user.supplier_rate, current_user.is_invoiced]
    daily_data = []
    days_data = []
    for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
        date1 = i - timedelta(days=1)
        date2 = i 
        warehouse_orders = connection.execute('SELECT count(warehouse_sale.id) as total_warehouse_sale_count FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
        warehouse_total_amount = connection.execute('SELECT sum(warehouse_sale.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
        day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
        day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
        day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0, int(warehouse_orders) if warehouse_orders is not None else 0, int(warehouse_total_amount) if warehouse_total_amount is not None else 0)
        daily_data.append(day_format)
        days_data.append(i.day)

    supplier_format.insert(4, (daily_data))
    suppliers_datas.append(supplier_format)

    form = DateSelect()

    if form.select_date.data is not None and form.validate_on_submit():

        suppliers_datas = []

        if form.select_date.data.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]

        supplier_format = [current_user.company_name, current_user.id, current_user.supplier_rate, current_user.is_invoiced]
        daily_data = []
        days_data = []
        for i in rrule(DAILY , dtstart=datetime.strptime(f'{form.select_date.data.year}-{form.select_date.data.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{form.select_date.data.year}-{form.select_date.data.month}-{end_day}', '%Y-%m-%d')):
            date1 = i - timedelta(days=1)
            date2 = i 
            warehouse_orders = connection.execute('SELECT count(warehouse_sale.id) as total_warehouse_sale_count FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
            warehouse_total_amount = connection.execute('SELECT sum(warehouse_sale.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
            day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
            day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": current_user.id}).scalar()
            day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0, int(warehouse_orders) if warehouse_orders is not None else 0, int(warehouse_total_amount) if warehouse_total_amount is not None else 0)
            daily_data.append(day_format)
            days_data.append(i.day)

        supplier_format.insert(4, (daily_data))
        suppliers_datas.append(supplier_format)
        return render_template('/supplier/supplier1/supplier_calculation_two_week.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form)

    return render_template('/supplier/supplier1/supplier_calculation_two_week.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form)