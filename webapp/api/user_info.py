from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from webapp.database import Connection
from webapp import models
from datetime import datetime
from webapp import bcrypt, models
import pytz

user_info_api = Blueprint('user_info_api', __name__)

@user_info_api.route('/api/user-info/update-password', methods = ["POST"])
@jwt_required()
def update_password():

    body = request.json
    connection = Connection()
    user_obj = connection.query(models.User).get(current_user.id)

    if not user_obj:
        return jsonify(msg="Хэрэглэгч олдсонгүй!", response = False), 400

    if user_obj.id != current_user.id:
        return jsonify(msg="Зөвшөөрөлгүй байна!", response = False), 400

    if bcrypt.check_password_hash(user_obj.password, body['current_password']):
        try:
            new = bcrypt.generate_password_hash(body['password'])
            user_obj.password = new
            connection.commit()
        except Exception:
            connection.rollback()
            return jsonify({
                "response": False,
                "msg": "Алдаа гарлаа!" }), 400
        else:
            return jsonify({
                    "response": True,
                    "msg": "Нууц үг амжилттай өөрчлөгдлөө."}), 200
    else:
        return jsonify(msg="Одоо ашиглагдаж байгаа нууц үг буруу байна!", response = False), 400


@user_info_api.route('/api/user-info/update-email', methods = ["POST"])
@jwt_required()
def update_profile_email():

    body = request.json
    connection = Connection()
    user_obj = connection.query(models.User).get(current_user.id)

    if not user_obj:
        return jsonify(msg="Хэрэглэгч олдсонгүй!", response = False), 400

    if user_obj.id != current_user.id:
        return jsonify(msg="Зөвшөөрөлгүй байна!", response = False), 400

    existing_user = connection.execute('select id from user where email = :email and id != :id', {'email': body['email'], 'id': user_obj.id}).first()

    if existing_user:
        return jsonify(msg="Цахим шуудан ашиглагдсан байна! Өөр цахим шуудан сонгоно уу!", response = False), 400

    try:
        user_obj.email = body['email']
        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify({
            "response": False,
            "msg": "Алдаа гарлаа!" }), 400
    else:
        return jsonify({
            "response": True,
            "msg": "Цахим шуудан амжилттай өөрчлөгдлөө."}), 200


@user_info_api.route('/api/user-info/update-phone', methods = ["POST"])
@jwt_required()
def update_profile_phone():

    body = request.json
    connection = Connection()
    user_obj = connection.query(models.User).get(current_user.id)

    if not user_obj:
        return jsonify(msg="Хэрэглэгч олдсонгүй!", response = False), 400

    if user_obj.id != current_user.id:
        return jsonify(msg="Зөвшөөрөлгүй байна!", response = False), 400

    existing_user = connection.execute('select id from user where phone = :phone and id != :id', {'phone': body['phone'], 'id': user_obj.id}).first()

    if existing_user:
        return jsonify(msg="Утасны дугаар өөр данс нь дээр бүртгэлтэй байна! Өөр Утасны дугаар сонгоно уу!", response = False), 400

    try:
        user_obj.phone = body['phone']
        connection.commit()
    except Exception:
        connection.rollback()
        return jsonify({
            "response": False,
            "msg": "Алдаа гарлаа!" }), 400
    else:
        return jsonify({
            "response": True,
            "msg": "Утасны дугаар амжилттай өөрчлөгдлөө."}), 200