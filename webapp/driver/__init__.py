def create_module(app, **kwargs):
    from .order import driver_order_blueprint

    app.register_blueprint(driver_order_blueprint)