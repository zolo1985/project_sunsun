from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz


accountant_order_blueprint = Blueprint('accountant_order', __name__)


@accountant_order_blueprint.route('/accountant/order-detail/<int:order_detail_id>', methods=['GET'])
@login_required
@has_role('accountant')
def accountant_order_detail(order_detail_id):
    connection = Connection()
    order_detail = connection.query(models.Delivery).get(order_detail_id)

    if not order_detail:
        flash('Хүргэлт олдсонгүй', 'danger')
        return redirect(url_for('manager_order.manager_orders_drivers_histories'))
