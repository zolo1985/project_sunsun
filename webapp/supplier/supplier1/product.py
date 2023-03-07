from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, abort)
from webapp import has_role
from flask_login import current_user, login_required
from webapp import models
from webapp.database import Connection
from webapp.supplier.supplier1.forms import ProductAddForm, ProductEditForm
from webapp.utils import add_and_resize_image
from sqlalchemy import desc


supplier1_product_blueprint = Blueprint('supplier1_product', __name__)


@supplier1_product_blueprint.route('/supplier1/products', methods=['GET', 'POST'])
@login_required
@has_role('supplier1')
def supplier1_products():
    connection = Connection()
    products = connection.query(models.Product).filter(models.Product.supplier_id==current_user.id).order_by(desc(models.Product.is_active)).all()
    return render_template('/supplier/supplier1/products.html', products=products)


@supplier1_product_blueprint.route('/supplier1/products/add', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_product_add():
    connection = Connection()
    form = ProductAddForm()

    if form.validate_on_submit():
        try:
            line_names = request.form.getlist("name")
            line_colors = request.form.getlist("color")
            line_sizes = request.form.getlist("size")
            line_types = request.form.getlist("type")
            line_descriptions = request.form.getlist("description")
            line_prices = request.form.getlist("price")
            line_usage_guides = request.form.getlist("usage_guide")
            line_images = request.files.getlist("image")

            for i, name in enumerate(line_names):
                product = models.Product()
                product.name = name.lower()
                product.color = line_colors[i].lower()
                product.size = line_sizes[i].lower()
                product.type = line_types[i].lower()
                product.price = line_prices[i]
                product.description = line_descriptions[i].lower()
                product.usage_guide = line_usage_guides[i].lower()

                if not line_images[i].filename == '':
                    product.image_url = add_and_resize_image(line_images[i]),
                
                current_user.products.append(product)
                connection.flush()

                inventory = models.Inventory()
                inventory.status = False
                inventory.product_id = product.id
                inventory.supplier_id = current_user.id

                connection.add(inventory)
                connection.commit()

        except Exception as ex:
            flash(f'%s'%(ex), 'danger')
            flash('Алдаа гарлаа', 'danger')
            connection.rollback()
            return redirect(url_for('supplier1_product.supplier1_products'))
        else:
            flash('Шинэ бараа агуулахад амжилттай нэмэгдлээ.', 'success')
            return redirect(url_for('supplier1_product.supplier1_products'))
    return render_template('/supplier/supplier1/product_add.html', form=form)


@supplier1_product_blueprint.route('/supplier1/products/edit/<int:product_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_product_edit(product_id):
    connection = Connection()
    product = connection.query(models.Product).get(product_id)

    if product is None:
        flash('Бараа олдсонгүй!', 'danger')
        return redirect(url_for('supplier1_product.supplier1_products'))

    if product.supplier_id != current_user.id:
        abort(403)

    form = ProductEditForm(product_id=product_id)

    if request.method == 'POST' and form.validate_on_submit():
        update_product = connection.query(models.Product).filter(models.Product.id==product.id).first()
        update_product.name = form.name.data.lower()
        update_product.color = form.color.data.lower()
        update_product.size = form.size.data.lower()
        update_product.type = form.type.data.lower()
        update_product.price = form.price.data
        update_product.description = form.description.data.lower()
        update_product.usage_guide = form.usage_guide.data.lower()

        image_file = request.files['image']

        if image_file:
            update_product.image_url = add_and_resize_image(image_file)

        try:
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('supplier1_product.supplier1_products'))
        else:
            flash('Бараа засагдлаа.', 'info')
            return redirect(url_for('supplier1_product.supplier1_products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.color.data = product.color
        form.size.data = product.size
        form.type.data = product.type
        form.description.data = product.description
        form.usage_guide.data = product.usage_guide
    return render_template('/supplier/supplier1/product_edit.html', form=form)


@supplier1_product_blueprint.route('/supplier1/products/state/<int:product_id>', methods=['GET','POST'])
@login_required
@has_role('supplier1')
def supplier1_product_state(product_id):
    connection = Connection()
    product = connection.query(models.Product).get(product_id)

    if product is None:
        flash('Бараа олдсонгүй!', 'danger')
        return redirect(url_for('supplier1_product.supplier1_products'))

    if product.supplier_id != current_user.id:
        abort(403)

    if product.is_active:
        product.is_active = False
    else:
        product.is_active = True

    try:
        connection.commit()
    except Exception:
        flash('Алдаа гарлаа!', 'danger')
        connection.rollback()
        return redirect(url_for('supplier1_product.supplier1_products'))
    else:
        flash('Төлөв өөрчлөгдлөө', 'info')
        return redirect(url_for('supplier1_product.supplier1_products'))