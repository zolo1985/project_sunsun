from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp.admin.forms import SupplierDateSelect, DateSelect
from webapp import models
from sqlalchemy import or_, text
from datetime import datetime, timedelta
from dateutil.rrule import DAILY,rrule
import calendar
import pytz

admin_supplier_calculation_blueprint = Blueprint('admin_supplier_calculation', __name__)

@admin_supplier_calculation_blueprint.route('/admin/supplier/calculation/daily', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_supplier_calculation_daily():
    connection = Connection()
    suppliers_delivery_total = []
    suppliers_warehouse_sales_total = []

    form = SupplierDateSelect()
    
    if form.validate_on_submit():
        selected_date = form.select_date.data
        selected_date_add_time = selected_date.strftime("%Y-%m-%d %H:%M:%S")
        datetime_object = datetime.strptime(selected_date_add_time, '%Y-%m-%d %H:%M:%S')
        selected_date_add_time_replace = datetime_object.replace(hour=17, minute=0)
        selected_date_time_minus_1day = selected_date_add_time_replace - timedelta(days=1)
        suppliers_delivery_total = connection.execute("SELECT supplier.company_name as supplier_name, GROUP_CONCAT(delivery.id) as delivery_ids, count(delivery.id) as total_delivery_count, sum(delivery.total_amount) as total_amount, supplier.is_invoiced as is_invoiced, supplier.supplier_rate as fee FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where delivery.received_from_clerk_date >= :yesterday and delivery.received_from_clerk_date < :selected_date and delivery.is_delivered=true group by supplier.id;", {"yesterday": selected_date_time_minus_1day, "selected_date": selected_date_add_time_replace}).all()
        suppliers_warehouse_sales_total = connection.execute("SELECT supplier.company_name as supplier_name, GROUP_CONCAT(warehouse_sale.id) as warehouse_sale_ids, count(warehouse_sale.id) as total_warehouse_sale_count, CAST(sum(warehouse_sale.total_amount) AS SIGNED) as total_amount, supplier.is_invoiced as is_invoiced, 0 as fee FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where warehouse_sale.created_date >= :yesterday and warehouse_sale.created_date < :selected_date and warehouse_sale.is_completed=true group by supplier.id;", {"yesterday": selected_date_time_minus_1day, "selected_date": selected_date_add_time_replace}).all()
        return render_template('/admin/supplier_calculation_daily.html', form=form, suppliers_delivery_total=suppliers_delivery_total, suppliers_warehouse_sales_total=suppliers_warehouse_sales_total)
    return render_template('/admin/supplier_calculation_daily.html', form=form, suppliers_delivery_total=suppliers_delivery_total, suppliers_warehouse_sales_total=suppliers_warehouse_sales_total)


@admin_supplier_calculation_blueprint.route('/admin/supplier/calculation/two-weeks', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_supplier_calculation_two_week():

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
    suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()
    
    suppliers_datas = []
    for supplier in suppliers:
        supplier_format = [supplier.company_name, supplier.id, supplier.supplier_rate, supplier.is_invoiced]
        daily_data = [(
            i.day,
            connection.execute('SELECT COUNT(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id WHERE (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true GROUP BY supplier.company_name;', {"date1": (i - timedelta(days=1)).replace(hour=17, minute=0), "date2": i.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar() or 0,
            connection.execute('SELECT SUM(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id WHERE (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true GROUP BY supplier.company_name;', {"date1": (i - timedelta(days=1)).replace(hour=17, minute=0), "date2": i.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar() or 0,
            connection.execute('SELECT COUNT(warehouse_sale.id) as total_warehouse_sale_count FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id WHERE (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true GROUP BY supplier.company_name;', {"date1": (i - timedelta(days=1)).replace(hour=17, minute=0), "date2": i.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar() or 0,
            connection.execute('SELECT SUM(warehouse_sale.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id WHERE (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true GROUP BY supplier.company_name;', {"date1": (i - timedelta(days=1)).replace(hour=17, minute=0), "date2": i.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar() or 0,
        ) for i in rrule(DAILY, dtstart=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{end_day}', '%Y-%m-%d'))]
        days_data = [i.day for i in rrule(DAILY, dtstart=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{selected_date.year}-{selected_date.month}-{end_day}', '%Y-%m-%d'))]

        supplier_format.insert(4, daily_data)
        suppliers_datas.append(supplier_format)

    return render_template('/admin/supplier_calculation_two_week.html', suppliers_datas=suppliers_datas, current_date=selected_date, day_list=days_data, form=form)

# @admin_supplier_calculation_blueprint.route('/admin/supplier/calculation/two-weeks', methods=['GET','POST'])
# @login_required
# @has_role('admin')
# def admin_supplier_calculation_two_week():

#     connection = Connection()
#     suppliers = connection.query(models.User).filter(or_(models.User.roles.any(models.Role.name=="supplier1"), models.User.roles.any(models.Role.name=="supplier2"))).all()

#     current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
#     suppliers_datas = []

#     if current_date.day <= 15:
#         start_day = 1
#         end_day = 15
#     else:
#         start_day = 16
#         end_day = calendar.monthrange(current_date.year, current_date.month)[1]

#     if form.validate_on_submit():
#         selected_date = form.select_date.data
#         if selected_date.day <= 15:
#             start_day = 1
#             end_day = 15
#         else:
#             start_day = 16
#             end_day = calendar.monthrange(selected_date.year, selected_date.month)[1]
#     else:
#         selected_date = current_date
#         if current_date.day <= 15:
#             start_day = 1
#             end_day = 15
#         else:
#             start_day = 16
#             end_day = calendar.monthrange(current_date.year, current_date.month)[1]

#     for supplier in suppliers:
#             supplier_format = [supplier.company_name, supplier.id, supplier.supplier_rate, supplier.is_invoiced]
#             daily_data = []
#             days_data = []
#             for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
#                 date1 = i - timedelta(days=1)
#                 date2 = i 
#                 warehouse_orders = connection.execute('SELECT count(warehouse_sale.id) as total_warehouse_sale_count FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 warehouse_total_amount = connection.execute('SELECT sum(warehouse_sale.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0, int(warehouse_orders) if warehouse_orders is not None else 0, int(warehouse_total_amount) if warehouse_total_amount is not None else 0)
#                 daily_data.append(day_format)
#                 days_data.append(i.day)

#             supplier_format.insert(4, (daily_data))
#             suppliers_datas.append(supplier_format)

#     form = DateSelect()

#     if form.select_date.data is not None and form.validate_on_submit():

#         suppliers_datas = []

#         if form.select_date.data.day <= 15:
#             start_day = 1
#             end_day = 15
#         else:
#             start_day = 16
#             end_day = calendar.monthrange(form.select_date.data.year, form.select_date.data.month)[1]

#         for supplier in suppliers:
#             supplier_format = [supplier.company_name, supplier.id, supplier.supplier_rate, supplier.is_invoiced]
#             daily_data = []
#             days_data = []
#             for i in rrule(DAILY , dtstart=datetime.strptime(f'{form.select_date.data.year}-{form.select_date.data.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{form.select_date.data.year}-{form.select_date.data.month}-{end_day}', '%Y-%m-%d')):
#                 date1 = i - timedelta(days=1)
#                 date2 = i 
#                 warehouse_orders = connection.execute('SELECT count(warehouse_sale.id) as total_warehouse_sale_count FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 warehouse_total_amount = connection.execute('SELECT sum(warehouse_sale.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.warehouse_sale as warehouse_sale on supplier.id=warehouse_sale.supplier_id where (warehouse_sale.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and warehouse_sale.is_completed=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 day_orders = connection.execute('SELECT count(delivery.id) as total_delivery_count FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 day_total_amount = connection.execute('SELECT sum(delivery.total_amount) as total_amount FROM sunsundatabase1.user as supplier join sunsundatabase1.delivery as delivery on supplier.id=delivery.user_id where (delivery.received_from_clerk_date BETWEEN :date1 AND :date2) and supplier.id=:supplier_id and delivery.is_delivered=true group by supplier.company_name;', {"date1": date1.replace(hour=17, minute=0), "date2": date2.replace(hour=17, minute=0), "supplier_id": supplier.id}).scalar()
#                 day_format = (i.day, int(day_orders) if day_orders is not None else 0, int(day_total_amount) if day_total_amount is not None else 0, int(warehouse_orders) if warehouse_orders is not None else 0, int(warehouse_total_amount) if warehouse_total_amount is not None else 0)
#                 daily_data.append(day_format)
#                 days_data.append(i.day)

#             supplier_format.insert(4, (daily_data))
#             suppliers_datas.append(supplier_format)
#         return render_template('/admin/supplier_calculation_two_week.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form)

#     return render_template('/admin/supplier_calculation_two_week.html', suppliers_datas=suppliers_datas, current_date=current_date, day_list=days_data, form=form)