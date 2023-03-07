def create_module(app, **kwargs):
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)