def create_module(app, **kwargs):
    from .handlers import error_blueprint
    app.register_blueprint(error_blueprint)