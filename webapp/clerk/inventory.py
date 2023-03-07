from flask import (Blueprint, render_template, request, jsonify)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from sqlalchemy import func, or_
from .forms import SupplierChooseForm, Supplier2ChooseForm
from webapp import models
from datetime import datetime
import calendar
import pytz
from dateutil.rrule import DAILY,rrule


clerk_inventory_blueprint = Blueprint('clerk_inventory', __name__)


@clerk_inventory_blueprint.route('/clerk/supplier1/inventories', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_inventories():
    current_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    connection = Connection()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).filter(models.User.is_authorized==True).all()

    inventories = []
    final_inventories = []
    days_data = []

    form = SupplierChooseForm()
    form.select_supplier.choices = [(supplier.id, f'%s'%(supplier.company_name)) for supplier in suppliers]
    form.select_supplier.choices.insert(0,(0,'Харилцагч сонгох'))

    if form.date.data is None and form.select_supplier.data != 0 and form.validate_on_submit():
        supplier = connection.query(models.User).filter(models.User.id==form.select_supplier.data).first()

        if current_date.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(current_date.year, current_date.month)[1]


        for product in supplier.products:
            data_format = [f"%s (%s, %s, %s)"%(product.name.capitalize(), "өнгөгүй" if product.color is None else product.color, "хэмжээгүй" if product.size is None else product.size, "төрөлгүй" if product.type is None else product.type), int(product.inventory.get_items())]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
                day_added = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, models.InventoryTransaction.transaction_type == 'inventory addition', func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
                day_expense = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, or_(models.InventoryTransaction.transaction_type == 'inventory subtraction', models.InventoryTransaction.transaction_type == 'delivery subtraction', models.InventoryTransaction.transaction_type == 'warehouse sale subtraction'), func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
                day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            data_format.insert(3, product.price)
            final_inventories.append(data_format)

        return render_template('/clerk/inventories.html', supplier=supplier, form=form, inventories=inventories, current_date=current_date, day_list=days_data, final_inventories=final_inventories)

    if form.date.data is not None and form.select_supplier.data != 0 and form.validate_on_submit():
        supplier = connection.query(models.User).filter(models.User.id==form.select_supplier.data).first()

        final_inventories = []
        days_data = []

        if form.date.data.day <= 15:
            start_day = 1
            end_day = 15
        else:
            start_day = 16
            end_day = calendar.monthrange(form.date.data.year, form.date.data.month)[1]

        for product in supplier.products:
            data_format = [f"%s (%s, %s, %s)"%(product.name.capitalize(), "өнгөгүй" if product.color is None else product.color, "хэмжээгүй" if product.size is None else product.size, "төрөлгүй" if product.type is None else product.type), int(product.inventory.get_items())]
            days_list = []
            days_data = []
            for i in rrule(DAILY , dtstart=datetime.strptime(f'{current_date.year}-{current_date.month}-{start_day}', '%Y-%m-%d'), until=datetime.strptime(f'{current_date.year}-{current_date.month}-{end_day}', '%Y-%m-%d')):
                day_added = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, models.InventoryTransaction.transaction_type == 'inventory addition', func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
                day_expense = connection.query(func.sum(models.InventoryTransaction.quantity)).join(models.Inventory).filter(models.Inventory.product_id == product.id, or_(models.InventoryTransaction.transaction_type == 'inventory subtraction', models.InventoryTransaction.transaction_type == 'delivery subtraction', models.InventoryTransaction.transaction_type == 'warehouse sale subtraction'), func.date(models.InventoryTransaction.transaction_date) == i.date()).scalar()
                day_format = (i.day, 0 if day_added is None else int(day_added), 0 if day_expense is None else int(day_expense))
                days_list.append(day_format)
                days_data.append(i.day)

            data_format.insert(2, (days_list))
            data_format.insert(3, product.price)
            final_inventories.append(data_format)

        return render_template('/clerk/inventories.html', supplier=supplier, form=form, inventories=inventories, current_date=form.date.data, day_list=days_data, final_inventories=final_inventories)
    return render_template('/clerk/inventories.html', form=form, inventories=inventories, current_date=current_date, day_list=days_data, final_inventories=final_inventories)



@clerk_inventory_blueprint.route('/clerk/supplier2/unstored-inventories', methods=['GET', 'POST'])
@login_required
@has_role('clerk')
def clerk_unstored_inventories():
    connection = Connection()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier2")).filter(models.User.is_authorized==True).all()
    form = Supplier2ChooseForm()
    form.select_supplier.choices = [(supplier.id, f'%s'%(supplier.company_name)) for supplier in suppliers]
    form.select_supplier.choices.insert(0,(0,'Харилцагч сонгох'))
    unstored_inventories = []
    
    if form.validate_on_submit():
        unstored_inventories = connection.query(models.UnstoredInventory).filter(models.UnstoredInventory.status==False, models.UnstoredInventory.supplier_id==form.select_supplier.data).all()
        return render_template('/clerk/unstored_inventories.html', unstored_inventories=unstored_inventories, form=form)

    return render_template('/clerk/unstored_inventories.html', unstored_inventories=unstored_inventories, form=form)