def create_module(app, **kwargs):
    from .order import driver_order_blueprint
    from .pickup_task import driver_pickup_task_blueprint
    from .return_task import driver_return_task_blueprint

    app.register_blueprint(driver_order_blueprint)
    app.register_blueprint(driver_pickup_task_blueprint)
    app.register_blueprint(driver_return_task_blueprint)