import base64
from datetime import datetime
import pytz

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from webapp import bcrypt, models
from webapp.database import Connection

auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/api/signin', methods=["POST"])
def signin():

    if 'Authorization' not in request.headers:
        return jsonify({
            "msg": "Мэдээлэл дутуу байна.",
            "response": False
        }), 400

    authorization = request.headers['Authorization']

    if not authorization.startswith('Basic '):
        return jsonify({
            "msg": "Мэдээлэл дутуу байна.",
            "response": False
        }), 400

    hashed_authorization = authorization[6:]
    decrypted = ""

    try:
        base64_bytes = hashed_authorization.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decrypted = message_bytes.decode('ascii')
    except Exception:
        return jsonify({
            "msg": "Нэвтрэх боломжгүй байна!",
            "response": False
        }), 400

    email = decrypted.split(":", maxsplit=2)[0].lower()
    password = decrypted.split(":", maxsplit=2)[1]

    connection = Connection()
    user = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver"), models.User.email==email).first()
    if user:
        if user.status != 'verified' and bcrypt.check_password_hash(user.password, password):
            connection.close()
            return jsonify({
                "msg": "Та дансаа баталгаажуулна уу!",
                "response": False
            }), 400
        elif user.is_authorized==False and bcrypt.check_password_hash(user.password, password):
            connection.close()
            return jsonify({
                "msg": "Таны дансыг түр хаасан байна. Менежертэй холбоо барина уу!",
                "response": False
            }), 400
        else:
            if user.status == 'verified' and user.is_authorized==True and bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(identity=user, fresh=True)
                refresh_token = create_refresh_token(identity=user)
                user.refresh_token = refresh_token
                user.last_login_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))

                connection.commit()
                connection.close()
                return jsonify({
                    "msg": "",
                    "response": True,
                    "user": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "id": str(user.id),
                        "username": user.firstname,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }), 200
            else:
                connection.close()
                return jsonify({
                    "msg": "Хэрэглэгч олдсонгүй!",
                    "response": False
                }), 400
            
    else:
        connection.close()
        return jsonify({
            "msg": "Хэрэглэгч олдсонгүй!",
            "response": False
        }), 400



@auth_api.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    connection = Connection()
    user = connection.query(models.User).filter_by(id=user_id).first()

    additional_claims = {"is_authorized": True}
    access_token = create_access_token(identity=user, additional_claims=additional_claims, fresh=False)

    connection.close()
    return jsonify(access_token=access_token)