from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models


pickups_api = Blueprint('pickups_api', __name__)

@pickups_api.route('/api/pickups', methods = ["GET", "POST"])
@jwt_required()
def pickups():
    connection = Connection()
    pickups = connection.query(models.PickupTask).filter(models.PickupTask.assigned_driver_id==current_user.id, models.PickupTask.is_completed==False, models.PickupTask.is_cancelled==False).all()

    payload = []
    for pickup in pickups:
        if pickup.supplier.has_role('supplier1'):
            payload.append({
            "id": pickup.id,
            "company_name": pickup.supplier.company_name.capitalize(),
            "quantity": len(pickup.pickup_task_details),
            "pickup_date": pickup.pickup_date.strftime("%Y-%m-%d"),
            "status": pickup.status,
            "type": "supplier1",
            "products": [{
                "name": task.product.name,
                "quantity": task.quantity,
                "size": task.product.size,
                "color": task.product.color,
                "type": task.product.type,
                } for task in pickup.pickup_task_details]})

        elif pickup.supplier.has_role('supplier2'):
            payload.append({
            "id": pickup.id,
            "company_name": pickup.supplier.company_name.capitalize(),
            "quantity": len(pickup.pickup_task_details),
            "pickup_date": pickup.pickup_date.strftime("%Y-%m-%d"),
            "status": pickup.status,
            "type": "supplier2",
            "products": [{
                "name": task.phone,
                "quantity": 1,
                } for task in pickup.pickup_task_details]})
    
    return jsonify(payload), 200
