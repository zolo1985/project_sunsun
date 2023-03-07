from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime
from sqlalchemy import func, or_
import pytz

orders_api = Blueprint('orders_api', __name__)

@orders_api.route('/api/orders', methods = ["GET", "POST"])
@jwt_required()
def orders():
    connection = Connection()
    orders = connection.query(models.Delivery).filter(models.Delivery.status == "assigned", models.Delivery.assigned_driver_id==current_user.id, models.Delivery.is_driver_received==True).all()

    payload = []
    for order in orders:
        if order.supplier_type == "stored":
            payload.append({
            "id": order.id,
            "order_received": order.is_received_from_clerk,
            "address": f'%s, %s, %s'%(order.addresses.district, order.addresses.khoroo, order.addresses.address) if order.destination_type == "local" else f'%s, %s'%(order.addresses.aimag, order.addresses.address),
            "phone": order.addresses.phone,
            "total_amount": order.total_amount,
            "company_name": order.user.company_name.capitalize(),
            "current_state": order.status,
            "delivery_date": order.delivery_date,
            "instruction": order.instruction,
            "products": [{
                "id": order_detail.products.id,
                "name": order_detail.products.name,
                "quantity": order_detail.quantity,
                "price": order_detail.products.price,
                "total_amount": order_detail.quantity * order_detail.products.price,
                "color": str(order_detail.products.color),
                "size": str(order_detail.products.size),
                "type": order_detail.products.type,
                "description": str(order_detail.products.description),
                "usage_guide": str(order_detail.products.usage_guide),
                "image": None if order_detail.products.image_url is None else ('http://%s/' % request.host) + 'api/image/' + order_detail.products.image_url
                } for order_detail in order.delivery_details]})

        elif order.supplier_type == "unstored":
            payload.append({
            "id": order.id,
            "address": f'%s, %s, %s'%(order.addresses.district, order.addresses.khoroo, order.addresses.address) if order.destination_type == "local" else f'%s, %s'%(order.addresses.aimag, order.addresses.address),
            "phone": order.addresses.phone,
            "order_received": order.is_received_from_clerk,
            "total_amount": order.total_amount,
            "company_name": order.user.company_name.capitalize(),
            "current_state": order.status,
            "delivery_date": order.delivery_date,
            "instruction": order.instruction,
            "products": []})

    return jsonify(payload), 200


@orders_api.route('/api/orders/modify-order', methods = ["GET", "POST"])
@jwt_required()
def modify_order():
    body = request.json
    connection = Connection()
    order = connection.query(models.Delivery).filter(models.Delivery.id==int(body["order_id"])).first()

    if not order:
        connection.close()
        return jsonify(msg="Хүргэлт олдсонгүй", response = False), 400

    try:
        if order.supplier_type=="stored":

            order.driver_comment = str(body["comment"])
            detail = connection.query(models.DeliveryDetail).filter(models.DeliveryDetail.delivery_id==order.id, models.DeliveryDetail.product_id==int(body["product_id"])).first()

            if not detail:
                return jsonify(msg="Бараа олдсонгүй", response = False), 400

            if detail.quantity < abs(int(body["quantity"])):
                return jsonify(msg="Барааны тоо ширхэг буруу байна", response = False), 400

            if detail.quantity == abs(int(body["quantity"])):
                if (detail.quantity * detail.products.price) > order.total_amount:
                    order.total_amount = 0
                else:
                    order.total_amount = order.total_amount - (detail.quantity * detail.products.price)

                driver_product_return = models.DriverProductReturn()
                driver_product_return.driver_id = current_user.id
                driver_product_return.delivery_id = order.id
                driver_product_return.product_id = detail.product_id
                driver_product_return.driver_comment = str(body["comment"])
                driver_product_return.product_quantity = abs(int(body["quantity"]))

                connection.add(driver_product_return)
                order.delivery_details.remove(detail)

            if detail.quantity > abs(int(body["quantity"])):
                if (abs(int(body["quantity"])) * detail.products.price) > order.total_amount:
                    order.total_amount = 0
                else:
                    order.total_amount = order.total_amount - (abs(int(body["quantity"])) * detail.products.price)

                driver_product_return = models.DriverProductReturn()
                driver_product_return.driver_id = current_user.id
                driver_product_return.delivery_id = order.id
                driver_product_return.product_id = detail.product_id
                driver_product_return.driver_comment = str(body["comment"])
                driver_product_return.product_quantity = abs(int(body["quantity"]))

                connection.add(driver_product_return)
                detail.quantity = detail.quantity - abs(int(body["quantity"]))

        else:
            return jsonify(msg="Алдаа гарлаа", response = False), 400

        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify(msg="Алдаа гарлаа", response = False), 400
    else:
        return jsonify(msg="Барааг хаслаа.", response = True), 200


@orders_api.route('/api/orders/completed', methods = ["POST"])
@jwt_required()
def order_completed():
    body = request.json
    connection = Connection()
    order = connection.query(models.Delivery).filter(models.Delivery.id==int(body["order_id"])).first()

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    if not order:
        return jsonify(msg="Хүргэлт олдсонгүй", response = False), 400

    if order.status == "completed" and order.is_delivered == True:
        return jsonify(msg="Хүргэлт хүргэгдсэн байна.", response = True), 200
    else:
        if order.supplier_type == "stored":
            order.status = "completed"
            order.is_delivered = True
            if len(body["driver_comment"]) > 5:
                order.driver_comment = body["driver_comment"]
            order.delivery_attempts = order.delivery_attempts + 1
            order.delivered_date = cur_date

            if order.is_postphoned:
                    if order.postphoned_date > cur_date:
                        order.postphoned_date = cur_date
                        order.delivery_date = cur_date

        elif order.supplier_type == "unstored":
            order.status = "completed"
            order.is_delivered = True
            if len(body["driver_comment"]) > 5:
                order.driver_comment = body["driver_comment"]
            order.delivery_attempts = order.delivery_attempts + 1
            order.delivered_date = cur_date

            if order.is_postphoned:
                    if order.postphoned_date > cur_date:
                        order.postphoned_date = cur_date
                        order.delivery_date = cur_date

        payment_detail = models.PaymentDetail()
        payment_detail.total_amount = int(body["total_amount"])
        payment_detail.comment = body["driver_comment"]

        job_history = models.DriverOrderHistory()
        job_history.status = "completed"
        job_history.delivery_id = order.id
        job_history.type = "delivery"
        job_history.driver_id = current_user.id
        job_history.supplier_name = order.user.company_name

        order.payment_details = payment_detail
        connection.add(job_history)

        try:
            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify(msg="Алдаа гарлаа", response = False), 400
        else:
            return jsonify(msg="Хүргэлт хүргэлээ.", response = True), 200


@orders_api.route('/api/orders/cancelled', methods = ["POST"])
@jwt_required()
def order_cancelled():
    body = request.json
    connection = Connection()
    order = connection.query(models.Delivery).filter(models.Delivery.id==int(body["order_id"])).first()

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

    if not order:
        connection.close()
        return jsonify(msg="Хүргэлт олдсонгүй", response = False), 400

    if order.status == "cancelled":
        return jsonify(msg="Хүргэлт цуцлагдсан байна.", response = True), 200
    else:
        try:
            if order.supplier_type == "stored":
                order.status = "cancelled"
                order.is_cancelled = True
                order.is_delivered = False
                order.driver_comment = body["driver_comment"]
                order.delivery_attempts = order.delivery_attempts + 1

                if order.is_postphoned:
                    if order.postphoned_date > cur_date:
                        order.postphoned_date = cur_date
                        order.delivery_date = cur_date

            elif order.supplier_type == "unstored":
                order.status = "cancelled"
                order.is_cancelled = True
                order.is_delivered = False
                order.driver_comment = body["driver_comment"]
                order.delivery_attempts = order.delivery_attempts + 1

                if order.is_postphoned:
                    if order.postphoned_date > cur_date:
                        order.postphoned_date = cur_date
                        order.delivery_date = cur_date

            job_history = models.DriverOrderHistory()
            job_history.created_date = cur_date
            job_history.status = "cancelled"
            job_history.driver_id = current_user.id
            job_history.type = "delivery"
            job_history.delivery_id = order.id
            job_history.supplier_name = order.user.company_name

            driver_return = models.DriverReturn()
            driver_return.delivery_status = "cancelled"
            driver_return.driver_id = current_user.id
            driver_return.delivery_id = order.id

            connection.add(driver_return)
            connection.add(job_history)

            connection.commit()
        except Exception as ex:
            print(ex)
            connection.rollback()
            return jsonify(msg="Алдаа гарлаа", response = False), 400
        else:
            return jsonify(msg="Хүргэлт цуцлагдлаа.", response = True), 200


@orders_api.route('/api/orders/postphoned', methods = ["POST"])
@jwt_required()
def order_postphoned():
    body = request.json
    connection = Connection()
    order = connection.query(models.Delivery).filter(models.Delivery.id==int(body["order_id"])).first()

    if not order:
        connection.close()
        return jsonify(msg="Хүргэлт олдсонгүй", response = False), 400

    if order.status == "unassigned" and order.is_postphoned == True:
        connection.close()
        return jsonify(msg="Хүргэлт хойшлогдлоо.", response = True), 200
    else:
        dt_naive = datetime.strptime(body["postphoned_date"], '%Y-%m-%d')
        timezone = pytz.timezone('Asia/Ulaanbaatar')
        dt_aware = timezone.localize(dt_naive)

        if order.supplier_type == "stored":
            order.status = "unassigned"
            order.postphoned_driver_id = current_user.id
            order.driver_comment = body["driver_comment"]
            order.is_postphoned = True
            order.is_delivered = False
            order.delivery_attempts = order.delivery_attempts + 1
            order.is_received_from_clerk = False
            order.is_driver_received = False
            order.assigned_driver_id = None
            order.postphoned_date = dt_aware
            order.delivery_date = dt_aware

        elif order.supplier_type == "unstored":
            order.status = "unassigned"
            order.postphoned_driver_id = current_user.id
            order.driver_comment = body["driver_comment"]
            order.is_postphoned = True
            order.is_delivered = False
            order.delivery_attempts = order.delivery_attempts + 1
            order.is_received_from_clerk = False
            order.is_driver_received = False
            order.assigned_driver_id = None
            order.postphoned_date = dt_aware
            order.delivery_date = dt_aware

        job_history = models.DriverOrderHistory()
        job_history.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        job_history.status = "postphoned"
        job_history.driver_id = current_user.id
        job_history.type = "delivery"
        job_history.delivery_id = order.id
        job_history.supplier_name = order.user.company_name

        driver_return = models.DriverReturn()
        driver_return.delivery_status = "postphoned"
        driver_return.driver_id = current_user.id
        driver_return.delivery_id = order.id

        connection.add(driver_return)
        connection.add(job_history)

        try:
            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify(msg="Алдаа гарлаа", response = False), 400
        else:
            return jsonify(msg="Хүргэлт хойшлогдлоо.", response = True), 200


@orders_api.route('/api/orders/histories', methods = ["GET", "POST"])
@jwt_required()
def order_histories():
    body = request.json
    connection = Connection()
    histories = connection.query(models.DriverOrderHistory).filter(models.DriverOrderHistory.driver_id==current_user.id).filter(models.DriverOrderHistory.status!="pickedup", models.DriverOrderHistory.status!="waiting", models.DriverOrderHistory.status!="enroute").filter(func.date(models.DriverOrderHistory.created_date) == (datetime.strptime(body["date"], "%Y-%m-%d")).date())
    payload = []
    for history in histories:
        if history.type == "delivery":
            if history.delivery.destination_type == "local":
                address = f'утас: %s, %s, %s, %s'%(history.delivery.addresses.phone, history.delivery.addresses.district, history.delivery.addresses.khoroo, history.delivery.addresses.address)
            elif history.delivery.destination_type == "long":
                address = f'утас: %s, %s, %s'%(history.delivery.addresses.phone, history.delivery.addresses.aimag, history.delivery.addresses.address)

            payload.append({
                "id": history.id,
                "address": address,
                "current_state": history.status,
                "type": history.type,
                "total_amount": str(history.delivery.total_amount),
            })
                
        elif history.type == "pickup":
            address = history.pickup_task.supplier.company_name

            payload.append({
                "id": history.id,
                "address": address,
                "current_state": history.status,
                "type": history.type,
                "total_amount": "0",
            })
        elif history.type == "return task":
            address = history.return_task.supplier.company_name

            payload.append({
                "id": history.id,
                "address": address,
                "current_state": history.status,
                "type": history.type,
                "total_amount": "0",
            })

    return jsonify(payload), 200



@orders_api.route('/api/orders/received-from-clerk', methods = ["POST"])
@jwt_required()
def order_received_from_clerk():
    body = request.json
    connection = Connection()
    order = connection.query(models.Delivery).filter(models.Delivery.id==body["order_id"]).first()

    if not order:
        return jsonify(msg="Хүргэлт олдсонгүй", response = False), 400

    if order.is_received_from_clerk == True:
        return jsonify(msg="Хүлээж авсан байна", response = True), 200

    if order.assigned_driver_id != current_user.id:
        return jsonify(msg="Таны Хүргэлт биш байна!", response = False), 400
    else:
        try:
            order.is_received_from_clerk = True
            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify(msg="Алдаа гарлаа", response = False), 400
        else:
            return jsonify(msg="Хүлээж авлаа", response = True), 200


@orders_api.route('/api/orders/orders-received-from-clerk', methods = ["POST"])
@jwt_required()
def orders_received_from_clerk():
    body = request.json
    connection = Connection()
    order_ids = []
    order_ids = body["orders"]

    for order in order_ids:
        order_to_update = connection.query(models.Delivery).get(int(order))
        if order_to_update.is_received_from_clerk == False:
            order_to_update.is_received_from_clerk = True
        else:
            continue

    try:
        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify(msg="Алдаа гарлаа", response = False), 400
    else:
        return jsonify(msg="Бүх хүргэлтийг хүлээж авлаа", response = True), 200
    


@orders_api.route('/api/orders/current-list', methods = ["POST"])
@jwt_required()
def orders_current_list():
    body = request.json

    connection = Connection()

    user = connection.query(models.User).get(current_user.id)

    if not user:
        connection.close()
        return jsonify(msg="Хэрэглэгч олдсонгүй", response = False), 400

    if user.is_authorized==False:
        connection.close()
        return jsonify(msg="Таны дансыг менежер хаасан байна! Менежертэй холбоо барина уу!", response = False), 400

    try:
        user.current_orders_list = body["current_orders_list"]
        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify(msg="Алдаа гарлаа", response = False), 400
    else:
        return jsonify(msg="Хүлээж авлаа", response = True), 200


@orders_api.route('/api/driver-stats', methods = ["GET", "POST"])
@jwt_required()
def driver_stats():
    connection = Connection()
    current_month_driver_stats = connection.execute("select COUNT(*) as total, driver_order_history.status as status from sunsundatabase2.driver_order_history where (driver_order_history.created_date between  DATE_FORMAT(NOW() ,'%Y-%m-01') AND NOW()) and driver_order_history.type='delivery' and driver_order_history.driver_id=:driver_id GROUP BY YEAR(driver_order_history.created_date), driver_order_history.status;", {'driver_id': current_user.id}).all()

    completed = 0
    postphoned = 0
    cancelled = 0

    for i, data in enumerate(current_month_driver_stats):
        if data["status"]=="completed":
            completed = data["total"]
        elif data["status"]=="cancelled":
            cancelled = data["total"]
        elif data["status"]=="postphoned":
            postphoned = data["total"]
        
    return jsonify({
        "completed": completed,
        "postphoned": postphoned,
        "cancelled": cancelled,
        "total": completed + postphoned + cancelled,
    }), 200
