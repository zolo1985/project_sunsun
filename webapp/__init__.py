import functools
import logging
import os
import redis
from flask import Flask, abort, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import AnonymousUserMixin, LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from webapp.database import init_db
from webapp import utils

class WebAnonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('flask_cors').level = logging.DEBUG

log = logging.getLogger(__name__)
bcrypt = Bcrypt()
login_manager = LoginManager()
jwt = JWTManager()
csrf = CSRFProtect()
cors = CORS()

login_manager.login_view = 'auth.signin'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'
login_manager.login_message = 'Хэрэглэгч нэвтрэх шаардлагатай!'
login_manager.anonymous_user = WebAnonymous


def create_app(object_name):
    app = Flask(__name__)
    utils.init_app(app)
    app._static_folder = os.path.abspath('webapp/static')
    app.config.from_object(object_name)
    
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)
    cors.init_app(app)
    init_db()

    from webapp.auth import create_module as auth_create_module
    from webapp.main import create_module as main_create_module
    from webapp.supplier.supplier1 import create_module as supplier1_create_module
    from webapp.supplier.supplier2 import create_module as supplier2_create_module
    from webapp.manager import create_module as manager_create_module
    from webapp.clerk import create_module as clerk_create_module
    from webapp.api import create_module as api_create_module
    from webapp.accountant import create_module as accountant_create_module
    from webapp.error import create_module as error_create_module
    from webapp.driver import create_module as driver_create_module

    auth_create_module(app)
    main_create_module(app)
    supplier1_create_module(app)
    supplier2_create_module(app)
    manager_create_module(app)
    clerk_create_module(app)
    api_create_module(app)
    accountant_create_module(app)
    error_create_module(app)
    driver_create_module(app)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.signin"))

def has_role(name):
    def real_decorator(f):
        def wraps(*args, **kwargs):
            if current_user.has_role(name):
                return f(*args, **kwargs)
            else:
                flash("Зөвшөөрөлгүй байна!", 'danger')
                abort(403)
        return functools.update_wrapper(wraps, f)
    return real_decorator