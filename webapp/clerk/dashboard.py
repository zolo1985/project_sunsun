from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz


clerk_dashboard_blueprint = Blueprint('clerk_dashboard', __name__)


@clerk_dashboard_blueprint.route('/clerk/dashboard', methods=['GET'])
@login_required
@has_role('clerk')
def clerk_dashboard():
    connection = Connection()
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    driver_pickups = connection.query(models.PickupTask).filter(models.PickupTask.is_driver_received==True, models.PickupTask.is_cancelled==False, models.PickupTask.is_completed==False).count()
    supplier_dropoffs = connection.query(models.SupplierDropoffTask).filter(models.SupplierDropoffTask.is_ready==True).count()
    unprocessed_orders = connection.execute("SELECT count(delivery.id) as total_count FROM sunsundatabase1.delivery as delivery join sunsundatabase1.user as driver on delivery.assigned_driver_id=driver.id WHERE DATE(delivery.delivery_date) =:cur_date and delivery.is_delivered=false and delivery.status='assigned' and delivery.is_received_from_clerk=false", {"cur_date": current_date.date()}).scalar()
    returns = connection.query(models.DriverReturn).filter(models.DriverReturn.is_returned==False).count()
    substracted_products = connection.query(models.DriverProductReturn).filter(models.DriverProductReturn.is_returned==False).count()
    unreturned_supplier2_orders = connection.query(models.UnstoredInventory).filter(models.UnstoredInventory.status==False, models.UnstoredInventory.is_returned_to_supplier==False).count()
    warehouse_sales = connection.query(models.WarehouseSale).filter(models.WarehouseSale.is_cancelled==False, models.WarehouseSale.is_completed==False).count()
    unprocessed_return_tasks = connection.query(models.ReturnTask).filter(models.ReturnTask.is_driver_received==False, models.ReturnTask.is_cancelled==False, models.ReturnTask.is_completed==False).count()
    return render_template('/clerk/dashboard.html', driver_pickups=driver_pickups, supplier_dropoffs=supplier_dropoffs, unprocessed_orders=unprocessed_orders, returns=returns, substracted_products=substracted_products, unreturned_supplier2_orders=unreturned_supplier2_orders, warehouse_sales=warehouse_sales, unprocessed_return_tasks=unprocessed_return_tasks)