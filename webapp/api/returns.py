from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models

returns_api = Blueprint('returns_api', __name__)

@returns_api.route('/api/returns', methods = ["GET", "POST"])
@jwt_required()
def returns():
    connection = Connection()
    driver_returns = connection.query(models.DriverReturn).filter(models.DriverReturn.is_returned==False, models.DriverReturn.driver_id==current_user.id).order_by(models.DriverReturn.created_date).all()
    substracted_products = connection.query(models.DriverProductReturn).filter(models.DriverProductReturn.is_returned==False, models.DriverProductReturn.driver_id==current_user.id).all()

    payload = []

    for driver_return in driver_returns:
        if driver_return.delivery.supplier_type == "unstored":
            payload.append({
            "id": driver_return.id,
            "company_name": driver_return.delivery.user.company_name.capitalize(),
            "address": f"утас: {driver_return.delivery.addresses.phone}, хаяг: {driver_return.delivery.addresses.address}",
            "status": driver_return.is_returned,
            "supplier_type": "unstored",
            "type": "delivery",
            "products": [{
                "name": driver_return.delivery.addresses.phone,
                "quantity": 1,
            }]})

        elif driver_return.delivery.supplier_type == "stored":
            payload.append({
            "id": driver_return.id,
            "company_name": driver_return.delivery.user.company_name.capitalize(),
            "address": f"утас: {driver_return.delivery.addresses.phone}, хаяг: {driver_return.delivery.addresses.address}",
            "status": driver_return.is_returned,
            "supplier_type": "stored",
            "type": "delivery",
            "products": [{
                "name": detail.products.name,
                "quantity": detail.quantity,
                "size": detail.products.size,
                "color": detail.products.color,
                "type": detail.products.type,
                } for detail in driver_return.delivery.delivery_details]})


    for substracted_product in substracted_products:
        payload.append({
            "id": substracted_product.id,
            "company_name": substracted_product.delivery.user.company_name.capitalize(),
            "address": f"утас: {substracted_product.delivery.addresses.phone}, хаяг: {substracted_product.delivery.addresses.address}",
            "status": substracted_product.is_returned,
            "supplier_type": "stored",
            "type": "substracted",
            "products": [{
                "name": substracted_product.product.name,
                "quantity": substracted_product.product_quantity,
                "size": substracted_product.product.size,
                "color": substracted_product.product.color,
                "type": substracted_product.product.type,
            }]})

    return jsonify(payload), 200

        
        


