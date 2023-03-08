def create_module(app, **kwargs):
    from .account import admin_account_blueprint
    from .profile import admin_profile_blueprint
    from .order import admin_order_blueprint
    from .statistic import admin_statistic_blueprint
    from .supplier_calculation import admin_supplier_calculation_blueprint

    app.register_blueprint(admin_account_blueprint)
    app.register_blueprint(admin_profile_blueprint)
    app.register_blueprint(admin_order_blueprint)
    app.register_blueprint(admin_supplier_calculation_blueprint)
    app.register_blueprint(admin_statistic_blueprint)