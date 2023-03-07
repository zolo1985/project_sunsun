def create_module(app, **kwargs):
    from .order import supplier2_order_blueprint
    from .driver_pickup import supplier2_driver_pickup_blueprint
    from .profile import supplier2_profile_blueprint
    from .search import supplier2_search_blueprint
    from .supplier_calculation import supplier2_calculation_blueprint
    from .return_task import supplier2_return_task_blueprint
    from .dashboard import supplier2_dashboard_blueprint

    app.register_blueprint(supplier2_order_blueprint)
    app.register_blueprint(supplier2_driver_pickup_blueprint)
    app.register_blueprint(supplier2_profile_blueprint)
    app.register_blueprint(supplier2_search_blueprint)
    app.register_blueprint(supplier2_calculation_blueprint)
    app.register_blueprint(supplier2_return_task_blueprint)
    app.register_blueprint(supplier2_dashboard_blueprint)