from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz


supplier1_dashboard_blueprint = Blueprint('supplier1_dashboard', __name__)


@supplier1_dashboard_blueprint.route('/supplier1/dashboard', methods=['GET'])
@login_required
@has_role('supplier1')
def supplier1_dashboard():
    connection = Connection()
    pickups = connection.query(func.count().label('pickups')).filter(models.PickupTask.supplier_id == current_user.id, models.PickupTask.is_ready==True).scalar()
    dropoffs = connection.query(func.count().label('dropoffs')).filter(models.SupplierDropoffTask.supplier_id == current_user.id, models.SupplierDropoffTask.is_ready==True).scalar()
    return render_template('/supplier/supplier1/dashboard.html', pickups=pickups, dropoffs=dropoffs)