def create_module(app, **kwargs):
    from .order import manager_order_blueprint
    from .pickup import manager_pickup_blueprint
    from .account import manager_account_blueprint
    from .search import manager_search_blueprint
    from .return_task import manager_return_task_blueprint
    from .profile import manager_profile_blueprint
    from .statistic import manager_statistic_blueprint
    from .dashboard import manager_dashboard_blueprint

    app.register_blueprint(manager_order_blueprint)
    app.register_blueprint(manager_pickup_blueprint)
    app.register_blueprint(manager_account_blueprint)
    app.register_blueprint(manager_search_blueprint)
    app.register_blueprint(manager_return_task_blueprint)
    app.register_blueprint(manager_profile_blueprint)
    app.register_blueprint(manager_statistic_blueprint)
    app.register_blueprint(manager_dashboard_blueprint)