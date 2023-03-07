from flask import (Blueprint, render_template)
from webapp import has_role
from flask_login import login_required, current_user
from webapp.database import Connection
from webapp import models
from webapp.supplier.supplier2.forms import SearchForm
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager
import pytz


supplier2_search_blueprint = Blueprint('supplier2_search', __name__)


@supplier2_search_blueprint.route('/supplier2/search', methods=["GET","POST"])
@login_required
@has_role('supplier2')
def search():
    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
    form = SearchForm()
    orders = []
    if form.validate_on_submit():
        connection = Connection()
        search_text = form.search_text.data
        orders = (
            connection.query(models.Delivery)
            .join(models.Address)
            .filter(models.Delivery.user_id==current_user.id, or_(
                models.Delivery.id.like(f'%{search_text}%'),
                models.Address.aimag.like(f'%{search_text}%'),
                models.Address.district.like(f'%{search_text}%'),
                models.Address.phone.like(f'%{search_text}%'),
                models.Address.address.like(f'%{search_text}%'),
                models.Address.phone_more.like(f'%{search_text}%')
            ))
            .options(contains_eager(models.Delivery.addresses))
            .limit(20)
        )

        # Bind parameters to prevent SQL injection
        orders = orders.params(search_text=search_text)
        return render_template('/supplier/supplier2/search.html', orders=orders, form=form, cur_date=cur_date)
    return render_template('/supplier/supplier2/search.html', orders=orders, form=form, cur_date=cur_date)