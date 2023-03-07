from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz


supplier2_dashboard_blueprint = Blueprint('supplier2_dashboard', __name__)


@supplier2_dashboard_blueprint.route('/supplier2/dashboard', methods=['GET'])
@login_required
@has_role('supplier2')
def supplier2_dashboard():
    connection = Connection()
    pickups = connection.query(func.count().label('pickups')).filter(models.PickupTask.supplier_id == current_user.id, models.PickupTask.is_ready==True).scalar()
    return_tasks = connection.query(func.count().label('return_tasks')).filter(models.ReturnTask.supplier_id==current_user.id, models.ReturnTask.is_ready==True).scalar()
    return render_template('/supplier/supplier2/dashboard.html', pickups=pickups, return_tasks=return_tasks)