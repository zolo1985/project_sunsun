def create_module(app, **kwargs):
    from .payment import accountant_payment_blueprint
    from .supplier_calculation import accountant_supplier_calculation_blueprint
    from .search import accountant_search_blueprint
    from .driver_salary import accountant_driver_salary_blueprint
    from .dashboard import accountant_dashboard_blueprint
    from .profile import accountant_profile_blueprint

    app.register_blueprint(accountant_payment_blueprint)
    app.register_blueprint(accountant_supplier_calculation_blueprint)
    app.register_blueprint(accountant_search_blueprint)
    app.register_blueprint(accountant_driver_salary_blueprint)
    app.register_blueprint(accountant_dashboard_blueprint)
    app.register_blueprint(accountant_profile_blueprint)