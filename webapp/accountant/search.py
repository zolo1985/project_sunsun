from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from webapp.accountant.forms import SearchForm
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
import pytz

accountant_search_blueprint = Blueprint('accountant_search', __name__)

@accountant_search_blueprint.route('/accountant/search', methods=["GET","POST"])
@login_required
@has_role('accountant')
def search():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = SearchForm()
    orders = []
    warehouse_sales = []
    if form.validate_on_submit():
        if form.search_types.data == 'Хүргэлт' and form.search_mode.data == "0":
            connection = Connection()
            search_text = form.search_text.data
            orders = (
                connection.query(models.Delivery)
                .join(models.Address)
                .filter(or_(
                    models.Address.aimag.like(f'%{search_text}%'),
                    models.Address.district.like(f'%{search_text}%'),
                    models.Address.phone.like(f'%{search_text}%'),
                    models.Address.address.like(f'%{search_text}%'),
                    models.Address.phone_more.like(f'%{search_text}%')
                ))
                .options(contains_eager(models.Delivery.addresses))
                .limit(20)
            )

            orders = orders.params(search_text=search_text)
            return render_template('/accountant/search.html', orders=orders, form=form, cur_date=cur_date, warehouse_sales=warehouse_sales)
        
        elif form.search_types.data == 'Хүргэлт' and form.search_mode.data == "1":
            connection = Connection()
            search_text = form.search_text.data
            orders = (
                connection.query(models.Delivery)
                .filter(models.Delivery.id==search_text)
                .limit(20)
            )

            # Bind parameters to prevent SQL injection
            orders = orders.params(search_text=search_text)
            return render_template('/accountant/search.html', orders=orders, form=form, cur_date=cur_date, warehouse_sales=warehouse_sales)

        elif form.search_types.data == 'Агуулах':
            connection = Connection()
            search_text = form.search_text.data
            warehouse_sales = (
                connection.query(models.WarehouseSale)
                .filter(models.WarehouseSale.id.like(f'%{search_text}%'))
                .limit(20)
            )

            # Bind parameters to prevent SQL injection
            warehouse_sales = warehouse_sales.params(search_text=search_text)
            return render_template('/accountant/search.html', orders=orders, form=form, cur_date=cur_date, warehouse_sales=warehouse_sales)
    return render_template('/accountant/search.html', orders=orders, form=form, cur_date=cur_date, warehouse_sales=warehouse_sales)