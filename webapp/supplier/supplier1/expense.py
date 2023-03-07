from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from datetime import datetime
from webapp.supplier.supplier1.forms import DateSelect
from sqlalchemy import func
import pytz

supplier1_expense_blueprint = Blueprint('supplier1_expense', __name__)

@supplier1_expense_blueprint.route('/supplier1/expenses', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_expenses():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    connection = Connection()
    orders = []
    warehouse_sales = []
    form = DateSelect()

    if form.validate_on_submit():
        if cur_date.date() <= form.select_date.data:
            orders = []
            orders_to_append = connection.query(models.Delivery).filter(models.Delivery.is_delivered==True, models.Delivery.user_id==current_user.id, func.date(models.Delivery.delivery_date)==form.select_date.data).all()
            for order_to_append in orders_to_append:
                if order_to_append.show_status:
                    orders.append(order_to_append)
            warehouse_sales = connection.query(models.WarehouseSale).filter(models.WarehouseSale.is_completed==True, func.date(models.WarehouseSale.created_date)==form.select_date.data).all()
        else:
            orders = connection.query(models.Delivery).filter(models.Delivery.is_delivered==True, models.Delivery.user_id==current_user.id, func.date(models.Delivery.delivery_date)==form.select_date.data).all()
            warehouse_sales = connection.query(models.WarehouseSale).filter(models.WarehouseSale.is_completed==True, func.date(models.WarehouseSale.created_date)==form.select_date.data).all()
        return render_template('/supplier/supplier1/expenses.html', orders=orders, form=form, warehouse_sales=warehouse_sales)

    return render_template('/supplier/supplier1/expenses.html', orders=orders, form=form, warehouse_sales=warehouse_sales)