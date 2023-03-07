def create_module(app, **kwargs):
    from .main import main_blueprint
    app.register_blueprint(main_blueprint)