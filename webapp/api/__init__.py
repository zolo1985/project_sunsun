from webapp import csrf, models
from functools import wraps
from webapp.database import Connection
from flask import jsonify, request

def create_module(app, **kwargs):
    from .orders import orders_api
    from .auth import auth_api
    from .utils import utils_api
    from .user_info import user_info_api
    from .pickups import pickups_api
    from .return_tasks import return_tasks_api
    from .returns import returns_api

    app.register_blueprint(orders_api)
    app.register_blueprint(auth_api)
    app.register_blueprint(utils_api)
    app.register_blueprint(user_info_api)
    app.register_blueprint(pickups_api)
    app.register_blueprint(return_tasks_api)
    app.register_blueprint(returns_api)

    csrf.exempt(orders_api)
    csrf.exempt(auth_api)
    csrf.exempt(utils_api)
    csrf.exempt(user_info_api)
    csrf.exempt(pickups_api)
    csrf.exempt(return_tasks_api)
    csrf.exempt(returns_api)



def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            if not 'Authorization' in request.headers:
               return jsonify(msg="token is missing.", response = False), 400

            data = request.headers['Authorization']
            token = str.replace(str(data), 'Bearer ','')
            try:
                connection = Connection()
                user = connection.query(models.User).filter_by(token=token).first()
                if not user:
                    connection.close()
                    return jsonify(msg="Хэрэглэгч олдсонгүй!", response = False), 400
                connection.close()
            except:
                return jsonify(msg="Хэрэглэгч олдсонгүй!", response = False), 400

            return f(user, *args, **kwargs)            
    return decorated_function