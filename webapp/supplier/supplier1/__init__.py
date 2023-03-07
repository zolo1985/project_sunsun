def create_module(app, **kwargs):
    from .order import supplier1_order_blueprint
    from .product import supplier1_product_blueprint
    from .utils import supplier1_util_blueprint
    from .driver_pickup import supplier1_driver_pickup_blueprint
    from .supplier_dropoff import supplier1_dropoff_blueprint
    from .inventory import supplier1_inventory_blueprint
    from .expense import supplier1_expense_blueprint
    from .search import supplier1_search_blueprint
    from .warehouse_sales import supplier1_warehouse_sales_blueprint
    from .supplier_calculation import supplier1_calculation_blueprint
    from .profile import supplier1_profile_blueprint
    from .dashboard import supplier1_dashboard_blueprint

    app.register_blueprint(supplier1_order_blueprint)
    app.register_blueprint(supplier1_product_blueprint)
    app.register_blueprint(supplier1_util_blueprint)
    app.register_blueprint(supplier1_driver_pickup_blueprint)
    app.register_blueprint(supplier1_dropoff_blueprint)
    app.register_blueprint(supplier1_inventory_blueprint)
    app.register_blueprint(supplier1_expense_blueprint)
    app.register_blueprint(supplier1_search_blueprint)
    app.register_blueprint(supplier1_warehouse_sales_blueprint)
    app.register_blueprint(supplier1_calculation_blueprint)
    app.register_blueprint(supplier1_profile_blueprint)
    app.register_blueprint(supplier1_dashboard_blueprint)