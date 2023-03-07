from flask import (Blueprint, render_template, redirect, url_for, flash, request, jsonify)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime, time
from sqlalchemy import func
from .forms import FiltersForm, FilterDateForm
import pytz
from webapp.utils import is_time_between


clerk_expense_blueprint = Blueprint('clerk_expense', __name__)


@clerk_expense_blueprint.route('/clerk/expenses', methods=['GET','POST'])
@login_required
@has_role('clerk')
def clerk_driver_orders():
    connection = Connection()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    orders = []

    form = FiltersForm()
    form.drivers.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form.drivers.choices.insert(0,(0,'Жолооч сонгох'))

    unassigned_orders = connection.execute("SELECT count(delivery.id) as total_count, CONCAT(driver.lastname, ' ', driver.firstname) as driver_name FROM sunsundatabase1.delivery as delivery join sunsundatabase1.user as driver on delivery.assigned_driver_id=driver.id WHERE DATE(delivery.delivery_date) =:cur_date and delivery.is_delivered=false and delivery.status='assigned' and delivery.is_received_from_clerk=false group by delivery.assigned_driver_id, driver.id;", {"cur_date": cur_date.date()}).all()

    order_window = is_time_between(time(6,30), time(3,55))

    if form.drivers.data is not None and form.validate():
        if form.drivers.data!="0":
            user = connection.query(models.User).filter(models.User.id==form.drivers.data).first()
            if user is not None:
                orders = connection.query(models.Delivery).filter(models.Delivery.status=="assigned").filter(models.Delivery.assigned_driver_id==user.id).all()
            return render_template('/clerk/expenses.html', form=form, orders=orders, order_window=order_window)
        else:
            unassigned_orders = connection.execute("SELECT count(delivery.id) as total_count, CONCAT(driver.lastname, ' ', driver.firstname) as driver_name FROM sunsundatabase1.delivery as delivery join sunsundatabase1.user as driver on delivery.assigned_driver_id=driver.id WHERE DATE(delivery.delivery_date) =:cur_date and delivery.is_delivered=false and delivery.status='assigned' and delivery.is_received_from_clerk=false group by delivery.assigned_driver_id, driver.id;", {"cur_date": cur_date.date()}).all()
            return render_template('/clerk/expenses.html', form=form, unassigned_orders=unassigned_orders, order_window=order_window)

    return render_template('/clerk/expenses.html', form=form, orders=orders, unassigned_orders=unassigned_orders, order_window=order_window)


@clerk_expense_blueprint.route('/clerk/return-task/expenses', methods=['GET','POST'])
@login_required
@has_role('clerk')
def clerk_driver_return_task_orders():
    connection = Connection()
    return_tasks = []

    unreceived_return_tasks = connection.execute("SELECT count(return_task.id) as total_count, CONCAT(driver.lastname, ' ', driver.firstname) as driver_name FROM sunsundatabase1.return_task as return_task join sunsundatabase1.user as driver on return_task.assigned_driver_id=driver.id WHERE return_task.is_completed=false and return_task.is_cancelled=false and return_task.is_driver_received=false group by return_task.assigned_driver_id, driver.id;").all()
    drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).filter(models.User.is_authorized==True).all()

    form = FiltersForm()
    form.drivers.choices = [(driver.id, f'{driver.lastname[0].capitalize()}. {driver.firstname}') for driver in drivers]
    form.drivers.choices.insert(0,(0,'Жолооч сонгох'))

    if form.drivers.data is not None and form.validate():
        if form.drivers.data != "0":
            user = connection.query(models.User).filter(models.User.id==form.drivers.data).first()
            if user is not None:
                return_tasks = connection.query(models.ReturnTask).filter(models.ReturnTask.is_ready==True, models.ReturnTask.assigned_driver_id==user.id).all()
            return render_template('/clerk/return_task_expenses.html', form=form, return_tasks=return_tasks)
        else:
            unreceived_return_tasks = connection.execute("SELECT count(return_task.id) as total_count, CONCAT(driver.lastname, ' ', driver.firstname) as driver_name FROM sunsundatabase1.return_task as return_task join sunsundatabase1.user as driver on return_task.assigned_driver_id=driver.id WHERE return_task.is_completed=false and return_task.is_cancelled=false and return_task.is_driver_received=false group by return_task.assigned_driver_id, driver.id;").all()
            return render_template('/clerk/return_task_expenses.html', form=form, unreceived_return_tasks=unreceived_return_tasks)

    return render_template('/clerk/return_task_expenses.html', form=form, return_tasks=return_tasks, unreceived_return_tasks=unreceived_return_tasks)



@clerk_expense_blueprint.route('/clerk/expense/driver-order', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_driver_order():
    body = request.json
    connection = Connection()
    order_to_expense = connection.query(models.Delivery).get(int(body["order_id"]))

    if order_to_expense is None:
        return jsonify({"response": False, "msg": "Хүргэлт олдсонгүй!"}), 400

    if order_to_expense.status != "assigned":
        return jsonify({"response": False, "msg": "Алдаа гарлаа!"}), 400

    if order_to_expense.is_driver_received==True:
        return jsonify({"response": False, "msg": "Жолооч авсан байна!"}), 400

    try:
        order_to_expense.received_from_clerk_id = current_user.id
        order_to_expense.is_driver_received = True
        order_to_expense.received_from_clerk_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify({"response": False, "msg": "Алдаа гарлаа!"}), 400
    else:
        return jsonify({"response": True, "msg": "Хүлээлгэж өглөө"}), 200


@clerk_expense_blueprint.route('/clerk/expense/return-task', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_expense_return_task():
    body = request.json
    connection = Connection()
    return_task_to_expense = connection.query(models.ReturnTask).get(int(body["return_task_id"]))

    if return_task_to_expense is None:
        return jsonify({"response": False, "msg": "Буцаалт олдсонгүй!"}), 400

    if return_task_to_expense.is_driver_received==True:
        return jsonify({"response": False, "msg": "Жолооч авсан байна!"}), 400

    if return_task_to_expense.supplier.has_role('supplier1'):
        try:
            print("do something here #stored")
        except Exception:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"}), 400
        else:
            return jsonify({"response": True, "msg": "Хүлээж авлаа"}), 200

    elif return_task_to_expense.supplier.has_role('supplier2'):
        try:
            return_task_to_expense.status = "pickedup"
            return_task_to_expense.is_ready = False
            return_task_to_expense.clerk_id = current_user.id
            return_task_to_expense.is_driver_received = True
            return_task_to_expense.received_from_clerk_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"}), 400
        else:
            return jsonify({"response": True, "msg": "Хүлээлгэж өглөө"}), 200
    else:
        return jsonify({"response": False, "msg": "Хүргэлт алдаатай байна!"}), 400


@clerk_expense_blueprint.route('/clerk/warehouse/expenses', methods=['GET'])
@login_required
@has_role('clerk')
def clerk_warehouse_expenses():
    connection = Connection()
    warehouse_sales = connection.query(models.WarehouseSale).all()
    return render_template('/clerk/warehouse_expenses.html', warehouse_sales=warehouse_sales)


@clerk_expense_blueprint.route('/clerk/warehouse/expenses/<int:warehouse_sale_id>', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_warehouse_expense(warehouse_sale_id):
    connection = Connection()
    warehouse_sale = connection.query(models.WarehouseSale).filter(models.WarehouseSale.id==warehouse_sale_id, models.WarehouseSale.is_ready==True).first()

    if warehouse_sale is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))

    if warehouse_sale.is_completed is True or warehouse_sale.is_cancelled is True:
        flash('Ажил дууссан байна.', 'info')
        return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))

    if warehouse_sale.is_received_from_clerk is False:
        try:
            warehouse_sale.is_received_from_clerk = True
            warehouse_sale.is_ready = False
            warehouse_sale.is_completed = True
            warehouse_sale.received_from_clerk_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            warehouse_sale.clerk_id = current_user.id

            connection.commit()
        except Exception as ex:
            connection.rollback()
            flash('Алдаа гарлаа', 'danger')
            return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))
        else:
            flash('Хүлээлгэж өглөө', 'success')
            return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))


# @clerk_expense_blueprint.route('/clerk/warehouse/expenses/cancel/<int:warehouse_sale_id>', methods=['GET', 'POST'])
# @login_required
# @has_role('clerk')
# def clerk_warehouse_expense_cancel(warehouse_sale_id):
#     connection = Connection()
#     warehouse_sale = connection.query(models.WarehouseSale).filter(models.WarehouseSale.id==warehouse_sale_id, models.WarehouseSale.is_ready==True).first()

#     if warehouse_sale is None:
#         flash('Олдсонгүй', 'danger')
#         return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))

#     if warehouse_sale.is_completed is True or warehouse_sale.is_cancelled is True:
#         flash('Ажил дууссан байна.', 'info')
#         return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))

#     if warehouse_sale.is_received_from_clerk is False:
#         try:
#             # warehouse_sale.is_ready = False
#             # warehouse_sale.is_cancelled = True
#             # warehouse_sale.clerk_id = current_user.id

#             for warehouse_sale_detail in warehouse_sale.warehouse_sale_details:
#                 print(warehouse_sale_detail.product.name)

#             connection.commit()
#         except Exception as ex:
#             connection.rollback()
#             flash('Алдаа гарлаа', 'danger')
#             return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))
#         else:
#             flash('Цуцлагдлаа', 'success')
#             return redirect(url_for('clerk_expense.clerk_warehouse_expenses'))
