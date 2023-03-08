from flask import (Blueprint, render_template, redirect, url_for, flash, jsonify, request)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp.clerk.forms import FilterDateForm
from webapp import models
from datetime import datetime
from sqlalchemy import func
import pytz


clerk_returns_blueprint = Blueprint('clerk_returns', __name__)


@clerk_returns_blueprint.route('/clerk/returns', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_driver_returns():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()
    returns = connection.query(models.DriverReturn).filter(func.date(models.DriverReturn.created_date) == cur_date).order_by(models.DriverReturn.created_date).all()
    substracted_products = connection.query(models.DriverProductReturn).filter(func.date(models.DriverProductReturn.created_date) == cur_date).all()

    form = FilterDateForm()
    if form.validate_on_submit():
        returns = connection.query(models.DriverReturn).filter(func.date(models.DriverReturn.created_date) == form.date.data).order_by(models.DriverReturn.created_date).all()
        substracted_products = connection.query(models.DriverProductReturn).filter(func.date(models.DriverProductReturn.created_date) == form.date.data).all()
        return render_template('/clerk/returns.html', returns=returns, form=form, substracted_products=substracted_products)

    return render_template('/clerk/returns.html', returns=returns, form=form, substracted_products=substracted_products)


@clerk_returns_blueprint.route('/clerk/returns/postphoned', methods=['POST'])
@login_required
@has_role('clerk')
def clerk_postphoned_order_with_button():
    body = request.json
    connection = Connection()
    product_return = connection.query(models.DriverReturn).get(int(body["order_id"]))

    if product_return is None:
        return jsonify({"response": False, "msg": "Буцаалт олдсонгүй!"})

    if product_return.is_returned==True:
        return jsonify({"response": False, "msg": "Захиалгыг буцааж авсан байна!"})

    if product_return.delivery_status!="postphoned":
        return jsonify({"response": False, "msg": "Төлөв буруу байна!"})

    if product_return.delivery.supplier_type=="stored":
        try:
            # for detail in product_return.delivery.delivery_details:
            #     product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()
            #     product.inventory.add_items(int(detail.quantity), current_user.id)

            #     inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==detail.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
            #     inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

            product_return.is_returned = True
            product_return.returned_clerk_id = current_user.id
            product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            connection.commit()
        except Exception as ex:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"})
        else:
            return jsonify({"response": True, "msg": "Хүлээж авлаа"})

    elif product_return.delivery.supplier_type=="unstored":
        
        product_return.is_returned = True
        product_return.returned_clerk_id = current_user.id
        product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

        try:
            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"})
        else:
            return jsonify({"response": True, "msg": "Хүлээж авлаа"})
    else:
        return jsonify({"response": False, "msg": "Буцаалт алдаатай байна"})


@clerk_returns_blueprint.route('/clerk/returns/cancelled', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_cancelled_order_with_button():
    body = request.json
    connection = Connection()
    product_return = connection.query(models.DriverReturn).get(int(body["order_id"]))

    if product_return is None:
        return jsonify({"response": False, "msg": "Буцаалт олдсонгүй!"})

    if product_return.is_returned==True:
        return jsonify({"response": False, "msg": "Захиалгыг буцааж авсан байна!"})

    if product_return.delivery_status!="cancelled":
        return jsonify({"response": False, "msg": "Төлөв буруу байна!"})

    if product_return.delivery.supplier_type=="stored":
        try:
            for detail in product_return.delivery.delivery_details:
                product = connection.query(models.Product).filter(models.Product.id == int(detail.products.id)).first()
                product.inventory.add_items(int(detail.quantity), current_user.id)
                inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==detail.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
                inventory_transaction.quantity = inventory_transaction.quantity - detail.quantity

            product_return.is_returned = True
            product_return.returned_clerk_id = current_user.id
            product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            connection.commit()
        except Exception as ex:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"})
        else:
            return jsonify({"response": True, "msg": "Хүлээж авлаа"})

    elif product_return.delivery.supplier_type=="unstored":
        try:
            product_return.is_returned = True
            product_return.returned_clerk_id = current_user.id
            product_return.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

            unstored_inventory = connection.query(models.UnstoredInventory).filter(models.UnstoredInventory.delivery_id==product_return.delivery.id).first()

            unstored_inventory.status = False
            unstored_inventory.comment = "Order cancelled"

            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify({"response": False, "msg": "Алдаа гарлаа!"})
        else:
            return jsonify({"response": True, "msg": "Хүлээж авлаа"})
    else:
        return jsonify({"response": False, "msg": "Буцаалт алдаатай байна"}), 400


@clerk_returns_blueprint.route('/clerk/returns/substracted', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_substracted_order_with_button():
    body = request.json
    connection = Connection()
    product_to_substract = connection.query(models.DriverProductReturn).get(int(body["order_id"]))

    if product_to_substract is None:
        return jsonify({"response": False, "msg": "Буцаалт олдсонгүй!"})

    if product_to_substract.is_returned==True:
        return jsonify({"response": False, "msg": "Барааг буцааж авсан байна!"})

    try:
        product = connection.query(models.Product).filter(models.Product.id == int(product_to_substract.product_id)).first()
        product.inventory.add_items(int(product_to_substract.product_quantity), current_user.id)
        inventory_transaction = connection.query(models.InventoryTransaction).filter(models.InventoryTransaction.delivery_id==product_to_substract.delivery_id, models.InventoryTransaction.inventory_id==product.inventory.id).first()
        inventory_transaction.quantity = inventory_transaction.quantity - product_to_substract.product_quantity

        product_to_substract.is_returned = True
        product_to_substract.returned_clerk_id = current_user.id
        product_to_substract.returned_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify({"response": False, "msg": "Алдаа гарлаа!"})
    else:
        return jsonify({"response": True, "msg": "Хүлээж авлаа"})