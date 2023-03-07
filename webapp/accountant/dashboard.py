from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz


accountant_dashboard_blueprint = Blueprint('accountant_dashboard', __name__)


@accountant_dashboard_blueprint.route('/accountant/dashboard', methods=['GET'])
@login_required
@has_role('accountant')
def accountant_dashboard():
    connection = Connection()
    unprocessed_orders = connection.execute("SELECT count(delivery.id) as total_count, CONCAT(driver.lastname, ' ', driver.firstname) as driver_name FROM sunsundatabase1.delivery as delivery join sunsundatabase1.user as driver on delivery.assigned_driver_id=driver.id WHERE delivery.is_processed_by_accountant=false and delivery.is_delivered=true and delivery.status='completed' group by delivery.assigned_driver_id;").all()
    unprocessed_warehouse_sales_count = connection.query(func.count()).filter(models.WarehouseSale.is_cancelled==False, models.WarehouseSale.is_processed_by_accountant==False).scalar()
    return render_template('/accountant/dashboard.html', unprocessed_orders=unprocessed_orders, unprocessed_warehouse_sales_count=unprocessed_warehouse_sales_count)