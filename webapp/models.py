
from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, PickleType,
                        Table, Text, Unicode)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList

from flask_login import current_user
from webapp import bcrypt, jwt
from webapp.database import Base
from datetime import datetime
import pytz
from sqlalchemy import event
from sqlalchemy.dialects.mysql import ENUM


def get_ulaanbaatar_time():
    return datetime.now(pytz.timezone("Asia/Ulaanbaatar"))


roles_table = Table('role_users', Base.metadata,
    Column('user_id', ForeignKey('user.id')),
    Column('role_id', ForeignKey('role.id')))

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)

    name                                = Column(Unicode(255))
    description                         = Column(Unicode(255), default='user')
    modified_by                         = Column(Integer, nullable=True)

    users = relationship("User",
            secondary=roles_table,
            back_populates="roles")
    

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}'.format(self.name)



class PickupTask(Base):
    __tablename__ = 'pickup_task'

    id = Column(Integer, primary_key=True)

    status                                  = Column(Unicode(255))
    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    is_driver_received                      = Column(Boolean, default=False)
    is_cancelled                            = Column(Boolean, default=False)
    comment                                 = Column(Text)
    
    pickup_date                             = Column(DateTime)
    clerk_received_date                     = Column(DateTime)
    created_date                            = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                           = Column(DateTime, onupdate=get_ulaanbaatar_time)

    assigned_driver_id                      = Column(Integer, ForeignKey('user.id'))
    assigned_manager_id                     = Column(Integer, ForeignKey('user.id'))
    received_clerk_id                       = Column(Integer, ForeignKey('user.id'))
    supplier_id                             = Column(Integer, ForeignKey('user.id'))
    modified_by                             = Column(Integer, nullable=True)

    supplier = relationship("User", back_populates="pickup_tasks", foreign_keys=[supplier_id])
    driver = relationship("User", back_populates="pickup_tasks", foreign_keys=[assigned_driver_id])
    manager = relationship("User", back_populates="pickup_tasks", foreign_keys=[assigned_manager_id])
    clerk = relationship("User", back_populates="pickup_tasks", foreign_keys=[received_clerk_id])
    pickup_task_details = relationship("PickupTaskDetail", back_populates="pickup_task")
    pickup_task_histories = relationship("DriverOrderHistory", back_populates="pickup_task")


class PickupTaskDetail(Base):
    __tablename__ = 'pickup_task_detail'

    id = Column(Integer, primary_key=True)

    quantity                                 = Column(Integer, nullable=False, default=0)
    
    phone                                    = Column(Unicode(255))
    phone_more                               = Column(Unicode(255))
    district                                 = Column(Unicode(255))
    khoroo                                   = Column(Unicode(255))
    aimag                                    = Column(Unicode(255))
    address                                  = Column(Unicode(255))
    total_amount                             = Column(Integer, nullable=False, default = 0)
    destination_type                         = Column(Unicode(255))
    comment                                  = Column(Text)
    
    product_id                               = Column(Integer, ForeignKey('product.id'))
    pickup_task_id                           = Column(Integer, ForeignKey('pickup_task.id'))
    modified_by                              = Column(Integer, nullable=True)

    pickup_task = relationship("PickupTask", back_populates="pickup_task_details")
    product = relationship("Product", back_populates="pickup_task_products")



class DropoffTask(Base):
    __tablename__ = 'dropoff_task'

    id = Column(Integer, primary_key=True)

    status                                  = Column(Unicode(255))
    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    is_driver_received                      = Column(Boolean, default=False)
    is_cancelled                            = Column(Boolean, default=False)
    comment                                 = Column(Text)

    received_from_clerk_date                = Column(DateTime)
    supplier_received_date                  = Column(DateTime)
    created_date                            = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                           = Column(DateTime, onupdate=get_ulaanbaatar_time)

    assigned_driver_id                      = Column(Integer, ForeignKey('user.id'))
    assigned_manager_id                     = Column(Integer, ForeignKey('user.id'))
    clerk_id                                = Column(Integer, ForeignKey('user.id'))
    supplier_id                             = Column(Integer, ForeignKey('user.id'))
    modified_by                             = Column(Integer, nullable=True)

    supplier = relationship("User", back_populates="dropoff_tasks", foreign_keys=[supplier_id])
    driver = relationship("User", back_populates="dropoff_tasks", foreign_keys=[assigned_driver_id])
    manager = relationship("User", back_populates="dropoff_tasks", foreign_keys=[assigned_manager_id])
    clerk = relationship("User", back_populates="dropoff_tasks", foreign_keys=[clerk_id])
    dropoff_task_details = relationship("DropoffTaskDetail", back_populates="dropoff_task")
    dropoff_task_histories = relationship("DriverOrderHistory", back_populates="dropoff_task")

    
class DropoffTaskDetail(Base):
    __tablename__ = 'dropoff_task_detail'

    id = Column(Integer, primary_key=True)

    quantity                                 = Column(Integer, nullable=False, default=0)
    phone                                    = Column(Unicode(255))

    product_id                               = Column(Integer, ForeignKey('product.id'))
    dropoff_task_id                          = Column(Integer, ForeignKey('dropoff_task.id'))
    modified_by                             = Column(Integer, nullable=True)

    dropoff_task = relationship("DropoffTask", back_populates="dropoff_task_details")


class ReturnTask(Base):
    __tablename__ = 'return_task'

    id = Column(Integer, primary_key=True)

    status                                  = Column(Unicode(255))
    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    is_driver_received                      = Column(Boolean, default=False)
    is_cancelled                            = Column(Boolean, default=False)
    comment                                 = Column(Text)

    supplier_received_date                  = Column(DateTime)
    received_from_clerk_date                = Column(DateTime)             
    created_date                            = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                           = Column(DateTime, onupdate=get_ulaanbaatar_time)

    assigned_driver_id                      = Column(Integer, ForeignKey('user.id'))
    assigned_manager_id                     = Column(Integer, ForeignKey('user.id'))
    clerk_id                                = Column(Integer, ForeignKey('user.id'))
    supplier_id                             = Column(Integer, ForeignKey('user.id'))
    modified_by                             = Column(Integer, nullable=True)

    return_task_details = relationship("ReturnTaskDetail", back_populates="return_task")
    supplier = relationship("User", back_populates="returns_tasks", foreign_keys=[supplier_id])
    driver = relationship("User", back_populates="returns_tasks", foreign_keys=[assigned_driver_id])
    manager = relationship("User", back_populates="returns_tasks", foreign_keys=[assigned_manager_id])
    clerk = relationship("User", back_populates="returns_tasks", foreign_keys=[clerk_id])
    return_task_histories = relationship("DriverOrderHistory", back_populates="return_task")


class ReturnTaskDetail(Base):
    __tablename__ = 'return_task_detail'

    id = Column(Integer, primary_key=True)

    quantity                                 = Column(Integer, nullable=False, default=0)
    phone                                    = Column(Unicode(255))

    product_id                               = Column(Integer, ForeignKey('product.id'))
    return_task_id                          = Column(Integer, ForeignKey('return_task.id'))
    modified_by                             = Column(Integer, nullable=True)

    return_task = relationship("ReturnTask", back_populates="return_task_details")
    product = relationship("Product", back_populates="return_task_products")


class SupplierDropoffTask(Base):
    __tablename__ = 'supplier_dropoff_task'

    id = Column(Integer, primary_key=True)

    status                                  = Column(Unicode(255))
    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    is_cancelled                            = Column(Boolean, default=False)
    comment                                 = Column(Text)

    clerk_received_date                     = Column(DateTime)
    created_date                            = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                           = Column(DateTime, onupdate=get_ulaanbaatar_time)

    received_clerk_id                       = Column(Integer, ForeignKey('user.id'))
    supplier_id                             = Column(Integer, ForeignKey('user.id'))
    modified_by                             = Column(Integer, nullable=True)

    supplier = relationship("User", back_populates="supplier_dropoff_tasks", foreign_keys=[supplier_id])
    clerk = relationship("User", back_populates="supplier_dropoff_tasks", foreign_keys=[received_clerk_id])
    supplier_dropoff_task_details = relationship("SupplierDropoffTaskDetail", back_populates="supplier_dropoff_task")

    
class SupplierDropoffTaskDetail(Base):
    __tablename__ = 'supplier_dropoff_task_detail'

    id = Column(Integer, primary_key=True)

    quantity                                 = Column(Integer, nullable=False, default=0)

    product_id                               = Column(Integer, ForeignKey('product.id'))
    supplier_dropoff_task_id                 = Column(Integer, ForeignKey('supplier_dropoff_task.id'))
    modified_by                              = Column(Integer, nullable=True)

    supplier_dropoff_task = relationship("SupplierDropoffTask", back_populates="supplier_dropoff_task_details")
    product = relationship("Product", back_populates="supplier_dropoff_task_products")


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)

    phone                                    = Column(Text)
    phone_more                               = Column(Text)
    district                                 = Column(Unicode(255))
    khoroo                                   = Column(Unicode(255))
    city                                     = Column(Unicode(255))
    aimag                                    = Column(Unicode(255))
    address                                  = Column(Text)
    created_date                             = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                            = Column(DateTime, onupdate=get_ulaanbaatar_time)
    delivery_id                              = Column(Integer, ForeignKey("delivery.id"))
    modified_by                              = Column(Integer, nullable=True)

    delivery = relationship("Delivery", back_populates="addresses")


class Inventory(Base):
    __tablename__ = 'inventory'

    id                                        = Column(Integer, primary_key=True)

    quantity                                  = Column(Integer, nullable=False, default = 0)
    status                                    = Column(Boolean, default=True)
    is_warehoused                             = Column(Boolean, default=True)
    is_driver_received                        = Column(Boolean, default=True)
    comment                                   = Column(Text)
    
    received_date                             = Column(DateTime)
    modified_date                             = Column(DateTime, onupdate=get_ulaanbaatar_time)
    created_date                              = Column(DateTime, default=get_ulaanbaatar_time)

    received_clerk_id                         = Column(Integer, ForeignKey('user.id'))
    supplier_id                               = Column(Integer, ForeignKey('user.id'))
    product_id                                = Column(Integer, ForeignKey('product.id'))
    modified_by                               = Column(Integer, nullable=True)

    product = relationship("Product", back_populates="inventory")
    received_clerk = relationship("User", foreign_keys=[received_clerk_id])
    transactions = relationship("InventoryTransaction", back_populates="inventory")

    def add_items(self, amount, clerk_id):
        self.quantity += amount
        self.received_clerk_id = clerk_id
        self.received_date = get_ulaanbaatar_time()
        self.status = True

    def subtract_items(self, amount):
        if self.quantity - amount < 0:
            raise ValueError("Агуулахад байгаа барааны тоо хүрэлцэхгүй байна!")
        self.quantity -= amount

    def get_items(self):
        if self.status:
            return self.quantity
        else:
            return 0

    def add_dropoff_items(self, amount, clerk_id):
        self.quantity += amount
        self.received_clerk_id = clerk_id
        self.received_date = get_ulaanbaatar_time()
        self.is_driver_received = False
        self.status = True


class InventoryTransaction(Base):
    __tablename__ = 'inventory_transaction'

    id                                  = Column(Integer, primary_key=True)
    quantity                            = Column(Integer, nullable=False)
    comment                             = Column(Text)
    transaction_type                    = Column(ENUM('inventory addition', 'inventory subtraction', 'delivery addition', 'delivery subtraction', 'warehouse sale subtraction'), nullable=False)
    transaction_date                    = Column(DateTime, default=get_ulaanbaatar_time)
    inventory_id                        = Column(Integer, ForeignKey('inventory.id'))
    delivery_id                         = Column(Integer, ForeignKey('delivery.id'))
    modified_by                         = Column(Integer, nullable=True)

    inventory = relationship("Inventory", back_populates="transactions")


class UnstoredInventory(Base):
    __tablename__ = 'unstored_inventory'

    id = Column(Integer, primary_key=True)

    status                                    = Column(Boolean, default=True)
    is_returned_to_supplier                   = Column(Boolean, default=False)
    comment                                   = Column(Text)
    
    clerk_received_date                       = Column(DateTime)
    modified_date                             = Column(DateTime, onupdate=get_ulaanbaatar_time)
    created_date                              = Column(DateTime, default=get_ulaanbaatar_time)

    received_clerk_id                         = Column(Integer, ForeignKey('user.id'))
    supplier_id                               = Column(Integer, ForeignKey('user.id'))
    delivery_id                               = Column(Integer, ForeignKey('delivery.id'))
    modified_by                               = Column(Integer, nullable=True)

    received_clerk = relationship("User", foreign_keys=[received_clerk_id])
    delivery = relationship("Delivery", back_populates="unstored_inventories")


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)

    name                                    = Column(Unicode(255), nullable=False)
    is_active                               = Column(Boolean, default=True)
    color                                   = Column(Text)
    size                                    = Column(Text)
    type                                    = Column(Text)
    price                                   = Column(Integer, nullable=False, default = 0)
    description                             = Column(Text)
    usage_guide                             = Column(Text)
    image_url                               = Column(Unicode(255))
    created_date                            = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                           = Column(DateTime, onupdate=get_ulaanbaatar_time)
    
    supplier_id                             = Column(Integer, ForeignKey('user.id'))
    modified_by                             = Column(Integer, nullable=True)

    supplier = relationship("User", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    pickup_task_products = relationship("PickupTaskDetail", back_populates="product")
    return_task_products = relationship("ReturnTaskDetail", back_populates="product")
    supplier_dropoff_task_products = relationship("SupplierDropoffTaskDetail", back_populates="product")
    product_substracts = relationship("DriverProductReturn", back_populates="product")

    def __repr__(self):
        return '{}'.format(self.name)



class Delivery(Base):
    __tablename__ = 'delivery'

    id = Column(Integer, primary_key=True)

    status                                   = Column(Unicode(255))
    total_amount                             = Column(Integer, nullable=False, default=0)
    supplier_type                            = Column(Unicode(50))
    destination_type                         = Column(Unicode(255))
    region                                   = Column(Unicode(255))
    is_delivered                             = Column(Boolean, default=False)
    is_postphoned                            = Column(Boolean, default=False)
    is_cancelled                             = Column(Boolean, default=False)
    is_received_from_clerk                   = Column(Boolean, default=False)
    is_driver_received                       = Column(Boolean, default=False)
    is_processed_by_accountant               = Column(Boolean, default=False)
    is_manager_created                       = Column(Boolean, default=False)
    is_manager_cancelled                     = Column(Boolean, default=False)
    is_manager_postphoned                    = Column(Boolean, default=False)
    show_comment                             = Column(Boolean, default=False)
    show_status                              = Column(Boolean, default=False)
    delivery_attempts                        = Column(Integer, nullable=False, default=0)
    driver_comment                           = Column(Text)
    comment                                  = Column(Text)
    type                                     = Column(Text)
    instruction                              = Column(Text)
    
    created_date                             = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                            = Column(DateTime, onupdate=get_ulaanbaatar_time)
    delivery_date                            = Column(DateTime, nullable=False)
    received_from_clerk_date                 = Column(DateTime)
    postphoned_date                          = Column(DateTime)
    delivered_date                           = Column(DateTime)

    user_id                                  = Column(Integer, ForeignKey("user.id"))
    processed_accountant_id                  = Column(Integer, ForeignKey("user.id"))
    assigned_driver_id                       = Column(Integer, ForeignKey("user.id"))
    assigned_manager_id                      = Column(Integer, ForeignKey("user.id"))
    postphoned_driver_id                     = Column(Integer, ForeignKey("user.id"))
    received_from_clerk_id                   = Column(Integer, ForeignKey("user.id"))
    modified_by                              = Column(Integer, nullable=True)

    user = relationship("User", back_populates="deliveries", foreign_keys=[user_id])
    driver = relationship("User", back_populates="drivers", foreign_keys=[assigned_driver_id])
    postphoned_driver = relationship("User", back_populates="postphoned_drivers", foreign_keys=[postphoned_driver_id])
    processed_accountant = relationship("User", back_populates="processed_accountants", foreign_keys=[processed_accountant_id])
    delivery_details = relationship("DeliveryDetail")
    addresses = relationship("Address", back_populates="delivery", uselist=False)
    delivery_histories = relationship("DriverOrderHistory", back_populates="delivery")
    unstored_inventories = relationship("UnstoredInventory", back_populates="delivery")
    payment_details = relationship("PaymentDetail", back_populates="delivery", uselist=False)
    delivery_returns = relationship("DriverReturn", back_populates="delivery", uselist=False)
    delivery_subtracted_products = relationship("DriverProductReturn", back_populates="delivery")

    
class DeliveryDetail(Base):
    __tablename__ = 'delivery_detail'

    id = Column(Integer, primary_key=True)

    quantity                                 = Column(Integer, nullable=False, default=0)
    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))
    product_id                               = Column(Integer, ForeignKey('product.id'))
    modified_by                              = Column(Integer, nullable=True)

    products = relationship("Product")
    delivery = relationship("Delivery", back_populates="delivery_details")


class DriverOrderHistory(Base):
    __tablename__ = 'driver_order_history'

    id = Column(Integer, primary_key=True)

    supplier_name                   = Column(Unicode(255))
    type                            = Column(Unicode(50))
    status                          = Column(Unicode(50))

    created_date                    = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                   = Column(DateTime, onupdate=get_ulaanbaatar_time)
    modified_by                     = Column(Integer, nullable=True)
    
    delivery_id                     = Column(Integer, ForeignKey('delivery.id'))
    pickup_task_id                  = Column(Integer, ForeignKey('pickup_task.id'))
    dropoff_task_id                 = Column(Integer, ForeignKey('dropoff_task.id'))
    return_task_id                  = Column(Integer, ForeignKey('return_task.id'))
    driver_id                       = Column(Integer, ForeignKey('user.id'))
    
    delivery = relationship("Delivery", back_populates="delivery_histories")
    pickup_task = relationship("PickupTask", back_populates="pickup_task_histories")
    dropoff_task = relationship("DropoffTask", back_populates="dropoff_task_histories")
    return_task = relationship("ReturnTask", back_populates="return_task_histories")


class WarehouseSale(Base):
    __tablename__ = 'warehouse_sale'

    id                                      = Column(Integer, primary_key=True)

    is_ready                                = Column(Boolean, default=False)
    is_completed                            = Column(Boolean, default=False)
    is_cancelled                            = Column(Boolean, default=False)
    is_processed_by_accountant              = Column(Boolean, default=False)
    total_amount                            = Column(Integer, nullable=False, default=0)
    comment                                 = Column(Text)

    is_received_from_clerk                  = Column(Boolean, default=False)
    received_from_clerk_date                = Column(DateTime)    
    created_date                            = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                           = Column(DateTime, onupdate=get_ulaanbaatar_time)
    modified_by                             = Column(Integer, nullable=True)

    accountant_id                           = Column(Integer, ForeignKey("user.id"))
    supplier_id                             = Column(Integer, ForeignKey('user.id'))
    clerk_id                                = Column(Integer, ForeignKey('user.id'))
    manager_id                              = Column(Integer, ForeignKey('user.id'))

    clerk = relationship("User", foreign_keys=[clerk_id])
    supplier = relationship("User", foreign_keys=[supplier_id])
    accountant = relationship("User", back_populates="accountant_warehouse_sales", foreign_keys=[accountant_id])
    manager = relationship("User", back_populates="manager_warehouse_sales", foreign_keys=[manager_id])
    warehouse_sale_details = relationship("WarehouseSaleDetail", back_populates="warehouse_sale")
    payment_details = relationship("PaymentDetail", back_populates="warehouse_sale", uselist=False)


class WarehouseSaleDetail(Base):
    __tablename__ = 'warehouse_sale_detail'

    id                              = Column(Integer, primary_key=True)
    quantity                        = Column(Integer)
    modified_by                     = Column(Integer, nullable=True)

    product_id                      = Column(Integer, ForeignKey('product.id'))
    warehouse_sale_id               = Column(Integer, ForeignKey('warehouse_sale.id'))

    warehouse_sale = relationship("WarehouseSale", back_populates="warehouse_sale_details")
    products = relationship("Product")


class PaymentDetail(Base):
    __tablename__ = 'payment_detail'

    id = Column(Integer, primary_key=True)

    total_amount                             = Column(Integer, nullable=False, default=0)
    comment                                  = Column(Text)
    created_date                             = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                            = Column(DateTime, onupdate=get_ulaanbaatar_time)
    modified_by                              = Column(Integer, nullable=True)

    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))
    warehouse_sale_id                        = Column(Integer, ForeignKey('warehouse_sale.id'))

    delivery = relationship("Delivery", back_populates="payment_details")
    warehouse_sale = relationship("WarehouseSale", back_populates="payment_details")

    def __repr__(self):
        return f'Нийт: {self.total_amount}₮'


class DriverReturn(Base):
    __tablename__ = 'driver_return'

    id = Column(Integer, primary_key=True)

    is_returned                              = Column(Boolean, default=False)
    delivery_status                          = Column(Unicode(255))

    returned_date                            = Column(DateTime)
    created_date                             = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                            = Column(DateTime, onupdate=get_ulaanbaatar_time)
    modified_by                              = Column(Integer, nullable=True)

    returned_clerk_id                        = Column(Integer, ForeignKey('user.id'))
    driver_id                                = Column(Integer, ForeignKey('user.id'))
    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))

    driver = relationship("User", back_populates="returns", foreign_keys=[driver_id])
    returned_clerk = relationship("User", back_populates="clerk_received_returns", foreign_keys=[returned_clerk_id])
    delivery = relationship("Delivery", back_populates="delivery_returns")


class DriverProductReturn(Base):
    __tablename__ = 'driver_product_return'

    id = Column(Integer, primary_key=True)

    is_returned                              = Column(Boolean, default=False)
    product_quantity                         = Column(Integer)
    driver_comment                           = Column(Text)

    returned_date                            = Column(DateTime)
    created_date                             = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                            = Column(DateTime, onupdate=get_ulaanbaatar_time)
    modified_by                              = Column(Integer, nullable=True)

    returned_clerk_id                        = Column(Integer, ForeignKey('user.id'))
    driver_id                                = Column(Integer, ForeignKey('user.id'))
    delivery_id                              = Column(Integer, ForeignKey('delivery.id'))
    product_id                               = Column(Integer, ForeignKey('product.id'))

    driver = relationship("User", back_populates="product_returns", foreign_keys=[driver_id])
    returned_product_clerk = relationship("User", back_populates="clerk_received_product_returns", foreign_keys=[returned_clerk_id])
    delivery = relationship("Delivery", back_populates="delivery_subtracted_products")
    product = relationship("Product", back_populates="product_substracts")


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)

    total_amount                             = Column(Integer, nullable=False, default=0)
    remaining_amount                         = Column(Integer, nullable=False, default=0)
    comment                                  = Column(Text)
    delivery_ids                             = Column(MutableList.as_mutable(PickleType), default=[])

    received_date                            = Column(DateTime)
    date_of_payment                          = Column(DateTime)

    created_date                             = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                            = Column(DateTime, onupdate=get_ulaanbaatar_time)
    modified_by                              = Column(Integer, nullable=True)
    
    driver_id                                = Column(Integer, ForeignKey('user.id'))
    accountant_id                            = Column(Integer, ForeignKey('user.id'))
    
    accountant = relationship("User", back_populates="payments", foreign_keys=[accountant_id])
    driver = relationship("User", back_populates="driver_payments", foreign_keys=[driver_id])
   

class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)

    company_name                                 = Column(Unicode(255), nullable=False)
    firstname                                    = Column(Unicode(255), nullable=False)
    lastname                                     = Column(Unicode(255), nullable=False)
    password                                     = Column(Text)
    email                                        = Column(Unicode(255), unique=True)
    phone                                        = Column(Unicode(255), unique=True)
    phone_extra                                  = Column(Unicode(255))
    address                                      = Column(Text)
    status                                       = Column(Unicode(100))
    is_authorized                                = Column(Boolean, default=True)
    is_invoiced                                  = Column(Boolean, default=False)
    refresh_token                                = Column(Unicode(2000))
    current_orders_list                          = Column(MutableList.as_mutable(PickleType), default=[])
    avatar_id                                    = Column(Unicode(255))
    supplier_rate                                = Column(Integer, nullable=False, default = 3000)
    delivery_rate                                = Column(Integer, nullable=False, default = 3000)
    created_date                                 = Column(DateTime, default=get_ulaanbaatar_time)
    modified_date                                = Column(DateTime, onupdate=get_ulaanbaatar_time)
    last_login_date                              = Column(DateTime)
    modified_by                                  = Column(Integer, nullable=True)

    roles = relationship("Role", secondary=roles_table)
    deliveries = relationship("Delivery", back_populates="user", foreign_keys=[Delivery.user_id])
    products = relationship("Product", back_populates="supplier")
    pickup_tasks = relationship("PickupTask", back_populates="supplier", foreign_keys=[PickupTask.supplier_id])
    dropoff_tasks = relationship("DropoffTask", back_populates="supplier", foreign_keys=[DropoffTask.supplier_id])
    returns_tasks = relationship("ReturnTask", back_populates="supplier", foreign_keys=[ReturnTask.supplier_id])
    supplier_dropoff_tasks = relationship("SupplierDropoffTask", back_populates="supplier", foreign_keys=[SupplierDropoffTask.supplier_id])
    drivers = relationship("Delivery", back_populates="driver", foreign_keys=[Delivery.assigned_driver_id])
    manager_warehouse_sales = relationship("WarehouseSale", back_populates="manager", foreign_keys=[WarehouseSale.manager_id])
    clerk_received_returns = relationship("DriverReturn", back_populates="returned_clerk", foreign_keys=[DriverReturn.returned_clerk_id])
    clerk_received_product_returns = relationship("DriverProductReturn", back_populates="returned_product_clerk", foreign_keys=[DriverProductReturn.returned_clerk_id])
    returns = relationship("DriverReturn", back_populates="driver", foreign_keys=[DriverReturn.driver_id])
    product_returns = relationship("DriverProductReturn", back_populates="driver", foreign_keys=[DriverProductReturn.driver_id])
    postphoned_drivers = relationship("Delivery", back_populates="postphoned_driver", foreign_keys=[Delivery.postphoned_driver_id])
    processed_accountants = relationship("Delivery", back_populates="processed_accountant", foreign_keys=[Delivery.processed_accountant_id])
    accountant_warehouse_sales = relationship("WarehouseSale", back_populates="accountant", foreign_keys=[WarehouseSale.accountant_id])
    payments = relationship("Payment", back_populates="accountant", foreign_keys=[Payment.accountant_id])
    driver_payments = relationship("Payment", back_populates="driver", foreign_keys=[Payment.driver_id])

    def __repr__(self):
        return self.firstname

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True
    
    @property
    def is_active(self):
        return True

    
    @property
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return str(self.id)

    def has_role(self, name):
        for role in self.roles:
            if role.name == name:
                return True
        return False

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

def get_current_user_id():
    if current_user and current_user.is_authenticated:
        return current_user.id
    else:
        return None

def set_modified_by(mapper, connection, target):
    if get_current_user_id() is not None:
        target.modified_by = get_current_user_id()

for cls in Base.registry._class_registry.values():
    if hasattr(cls, '__tablename__'):
        event.listen(cls, 'before_update', set_modified_by)

