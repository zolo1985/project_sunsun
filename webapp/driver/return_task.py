from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models


driver_return_task_blueprint = Blueprint('driver_return_task', __name__)


@driver_return_task_blueprint.route('/driver/return-tasks')
@login_required
@has_role('driver')
def driver_return_tasks():
    connection = Connection()
    return_tasks = connection.query(models.ReturnTask).filter(models.ReturnTask.assigned_driver_id==current_user.id, models.ReturnTask.is_completed==False, models.ReturnTask.is_cancelled==False).all()
    return render_template('/driver/return_tasks.html', return_tasks=return_tasks)
