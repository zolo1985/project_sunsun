from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models

return_tasks_api = Blueprint('return_tasks_api', __name__)

@return_tasks_api.route('/api/return-tasks', methods = ["GET", "POST"])
@jwt_required()
def return_tasks():
    connection = Connection()
    return_tasks = connection.query(models.ReturnTask).filter(models.ReturnTask.assigned_driver_id==current_user.id).filter(models.ReturnTask.is_completed==False, models.ReturnTask.is_cancelled==False).all()

    payload = []
    for return_task in return_tasks:
        payload.append({
        "id": return_task.id,
        "company_name": return_task.supplier.company_name.capitalize(),
        "quantity": len(return_task.return_task_details),
        "return_task_date": return_task.created_date.strftime("%Y-%m-%d"),
        "status": return_task.status,
        "products": [{
            "name": task.phone,
            "quantity": 1,
            } for task in return_task.return_task_details]})
    
    return jsonify(payload), 200