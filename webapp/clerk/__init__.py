def create_module(app, **kwargs):
    from .receive import clerk_receive_blueprint
    from .expense import clerk_expense_blueprint
    from .returns import clerk_returns_blueprint
    from .inventory import clerk_inventory_blueprint
    from .search import clerk_search_blueprint
    from .dashboard import clerk_dashboard_blueprint
    from .return_task import clerk_return_task_blueprint
    from .profile import clerk_profile_blueprint

    app.register_blueprint(clerk_receive_blueprint)
    app.register_blueprint(clerk_expense_blueprint)
    app.register_blueprint(clerk_returns_blueprint)
    app.register_blueprint(clerk_inventory_blueprint)
    app.register_blueprint(clerk_search_blueprint)
    app.register_blueprint(clerk_dashboard_blueprint)
    app.register_blueprint(clerk_return_task_blueprint)
    app.register_blueprint(clerk_profile_blueprint)