from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models


driver_pickup_task_blueprint = Blueprint('driver_pickup_task', __name__)


@driver_pickup_task_blueprint.route('/driver/pickups')
@login_required
@has_role('driver')
def driver_pickup_tasks():
    connection = Connection()
    pickup_tasks = connection.query(models.PickupTask).filter(models.PickupTask.assigned_driver_id==current_user.id, models.PickupTask.is_completed==False, models.PickupTask.is_cancelled==False).all()
    return render_template('/driver/pickup_tasks.html', pickup_tasks=pickup_tasks)
