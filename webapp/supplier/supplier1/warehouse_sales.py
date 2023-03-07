from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import OrderAddForm, FiltersForm
from datetime import datetime, time, timedelta
from sqlalchemy import func, or_
from webapp.utils import is_time_between
import pytz


supplier1_warehouse_sales_blueprint = Blueprint('supplier1_warehouse_sales', __name__)


@supplier1_warehouse_sales_blueprint.route('/supplier1/warehouse-sales', methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_warehouse_sales():
    connection = Connection()
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = FiltersForm()
    warehouse_sales = []
    warehouse_sales = connection.query(models.WarehouseSale).filter(models.WarehouseSale.supplier_id==current_user.id, func.date(models.WarehouseSale.created_date)==cur_date.date()).all()

    if form.validate_on_submit() and form.date.data is not None:
        warehouse_sales = connection.query(models.WarehouseSale).filter(models.WarehouseSale.supplier_id==current_user.id, func.date(models.WarehouseSale.created_date)==form.date.data).all()
        return render_template('/supplier/supplier1/warehouse_sales.html', warehouse_sales=warehouse_sales, cur_date=cur_date, form=form)

    return render_template('/supplier/supplier1/warehouse_sales.html', warehouse_sales=warehouse_sales, cur_date=cur_date, form=form)
    