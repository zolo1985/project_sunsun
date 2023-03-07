from flask import (Blueprint, render_template, flash, request, redirect, url_for, jsonify)
from webapp import has_role
from flask_login import current_user, login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz


manager_dashboard_blueprint = Blueprint('manager_dashboard', __name__)


@manager_dashboard_blueprint.route('/manager/dashboard', methods=['GET'])
@login_required
@has_role('manager')
def manager_dashboard():
    connection = Connection()
    return render_template('/manager/dashboard.html')