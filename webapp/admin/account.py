from flask import (Blueprint, render_template, flash, redirect, url_for, abort, request)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from .forms import NewAccountForm, EditAccountForm, CreateAccountsFromExcelForm, CreateProductsFromExcelForm, SelectAccountTypeForm
from webapp import bcrypt
import pytz
import pandas as pd


admin_account_blueprint = Blueprint('admin_account', __name__)



@admin_account_blueprint.route('/admin/accounts', methods=['GET', 'POST'])
@login_required
@has_role('admin')
def accounts():
    connection = Connection()

    roles_selection = ['Менежер', 'Жолооч', 'Нягтлан', 'Нярав', 'Харилцагч(агуулахтай)', 'Харилцагч(агуулахгүй)']

    form = SelectAccountTypeForm()
    form.accounts.choices = [role for role in roles_selection]

    if form.validate_on_submit():
        drivers = []
        supplier1s = []
        supplier2s = []
        accountants = []
        clerks = []
        managers = []
        if form.accounts.data == 'Жолооч':
            drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
        elif form.accounts.data == 'Харилцагч(агуулахтай)':
            supplier1s = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).all()
        elif form.accounts.data == 'Харилцагч(агуулахгүй)':
            supplier2s = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier2")).all()
        elif form.accounts.data == 'Нягтлан':
            accountants = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="accountant")).all()
        elif form.accounts.data == 'Нярав':
            clerks = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="clerk")).all()
        elif form.accounts.data == 'Менежер':
            managers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="manager")).all()
        return render_template('/admin/accounts.html', drivers=drivers, clerks=clerks, accountants=accountants, supplier1s=supplier1s, supplier2s=supplier2s, managers=managers, form=form)
    return render_template('/admin/accounts.html', drivers=[], clerks=[], accountants=[], supplier1s=[], supplier2s=[], managers=[], form=form)


@admin_account_blueprint.route('/admin/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
@has_role('admin')
def account(account_id):

    connection = Connection()
    account = connection.query(models.User).get(account_id)

    if account is None:
        flash('Олдсонгүй', 'danger')
        connection.close()
        
    form = EditAccountForm()

    if form.validate_on_submit():
        account_to_update = connection.query(models.User).get(account_id)
        account_to_update.email = form.email.data
        account_to_update.phone = form.phone.data
        account_to_update.supplier_rate = form.supplier_rate.data

        try:
            connection.commit()
        except:
            connection.rollback()
            flash('Алдаа гарлаа', 'danger')
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Мэдээлэл өөрчлөгдлөө', 'success')
            return redirect(url_for('admin_account.accounts'))

    elif request.method == 'GET':
        form.email.data = account.email
        form.phone.data = account.phone
        form.supplier_rate.data = account.supplier_rate
        return render_template('/admin/account.html', form=form, account=account)
    return render_template('/admin/account.html', form=form, account=account)



@admin_account_blueprint.route('/admin/drivers/authorize/<int:driver_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_driver_authorize(driver_id):
    connection = Connection()
    user = connection.query(models.User).get(driver_id)

    if user.has_role('driver'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)


@admin_account_blueprint.route('/admin/supplier1/authorize/<int:supplier1_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_supplier1_authorize(supplier1_id):
    connection = Connection()
    user = connection.query(models.User).get(supplier1_id)

    if user.has_role('supplier1'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)



@admin_account_blueprint.route('/admin/supplier2/authorize/<int:supplier2_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_supplier2_authorize(supplier2_id):
    connection = Connection()
    user = connection.query(models.User).get(supplier2_id)

    if user.has_role('supplier2'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)



@admin_account_blueprint.route('/admin/managers/authorize/<int:manager_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_manager_authorize(manager_id):
    connection = Connection()
    user = connection.query(models.User).get(manager_id)

    if user.has_role('manager'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash(f'%s менежерийн төлөв өөрчлөгдлөө.'%(user.firstname), 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)



@admin_account_blueprint.route('/admin/clerks/authorize/<int:clerk_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_clerk_authorize(clerk_id):
    connection = Connection()
    user = connection.query(models.User).get(clerk_id)

    if user.has_role('clerk'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Няравын төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)


@admin_account_blueprint.route('/admin/accountants/authorize/<int:accountant_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_accountant_authorize(accountant_id):
    connection = Connection()
    user = connection.query(models.User).get(accountant_id)

    if user.has_role('accountant'):
        try:
            if user.is_authorized==True:
                user.is_authorized = False
            else:
                user.is_authorized = True
            
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Нягтлан бодогчийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)


@admin_account_blueprint.route('/admin/account/password-reset/<int:user_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_password_reset(user_id):
    connection = Connection()
    user = connection.query(models.User).get(user_id)

    if user:
        try:
            hashed_password = bcrypt.generate_password_hash("password")
            user.password = hashed_password
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            flash('Нууц үг password болж өөрчлөгдлөө.', 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        abort(403)


def switch_role(role):
    if role == "Харилцагч(агуулахгүй)":
        return "supplier1"
    elif role == "Харилцагч(агуулахтай)":
        return "supplier2"
    elif role == "Жолооч":
        return "driver"
    elif role == "Нягтлан":
        return "accountant"
    elif role == "Нярав":
        return "clerk"
    elif role == "Менежер":
        return "manager"


@admin_account_blueprint.route('/admin/accounts/add-account', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_add_account():
    form = NewAccountForm()
    connection = Connection()
    roles_selection = ['Менежер', 'Нягтлан', 'Нярав', 'Харилцагч(агуулахгүй)', 'Харилцагч(агуулахтай)', 'Жолооч']
    form.select_user_role.choices = [(role) for role in roles_selection]
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            user = models.User()
            user.company_name = form.company_name.data.lower()
            user.firstname = form.firstname.data.lower()
            user.lastname = form.lastname.data.lower()
            user.password = hashed_password
            user.status = "verified"
            user.email = form.email.data
            user.phone = form.phone.data
            user_role = connection.query(models.Role).filter_by(name=switch_role(form.select_user_role.data)).first()
            user.roles.append(user_role)
            user.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            user.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
            user.is_authorized = True
            connection.add(user)
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.admin_add_account'))
        else:
            flash('Шинэ данс үүслээ баталгаажуулах и-мэйл илгээлээ.', 'success')
            return redirect(url_for('admin_account.admin_add_account'))

    return render_template('/admin/new_account.html', form=form)


@admin_account_blueprint.route('/admin/account/is-invoiced/<int:user_id>', methods=['GET','POST'])
@login_required
@has_role('admin')
def admin_is_invoiced(user_id):
    connection = Connection()
    user = connection.query(models.User).get(user_id)

    if user:
        try:
            if user.is_invoiced:
                user.is_invoiced = False
            else:
                user.is_invoiced = True

            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('admin_account.accounts'))
        else:
            if user.is_invoiced:
                flash(f'%s нэхэмжилдэггүй боллоо.'%(user.company_name), 'success')
            else:
                flash(f'%s нэхэмжилдэг боллоо.'%(user.company_name), 'success')
            return redirect(url_for('admin_account.accounts'))
    else:
        flash('Хэрэглэгч олдсонгүй!', 'danger')
        return redirect(url_for('admin_account.accounts'))



@admin_account_blueprint.route('/admin/accounts/from-excel', methods=['GET', 'POST'])
@login_required
@has_role('admin')
def accounts_from_excel():

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    form = CreateAccountsFromExcelForm()
    accounts_to_add = []
    connection = Connection()

    if form.validate_on_submit():
        if len(request.files) > 0 and request.files['excel_file'].filename != "":
            excel_file = request.files['excel_file']
            df = pd.read_excel(excel_file)

            company_names = df['company name'].values
            lastnames = df['lastname'].values
            firstnames = df['firstname'].values
            phones = df['phone'].values
            extra_phones = df['phone extra'].values
            emails = df['email'].values
            addresses = df['address'].values
            warehoused = df['warehoused'].values

            for i, company_name in enumerate(company_names):
                if (str(company_name) != 'nan') and (str(lastnames[i]) != 'nan') and (str(firstnames[i]) != 'nan') and (str(phones[i]) != 'nan') and (str(emails[i]) != 'nan') and (str(warehoused[i]) != 'nan'):
                    accoount_dict = {
                        "company_name": company_name,
                        "firstname": firstnames[i],
                        "lastname": lastnames[i],
                        "phone": phones[i],
                        "phone_extra": None if str(extra_phones[i]) == 'nan' else str(extra_phones[i]),
                        "email": emails[i],
                        "address": None if str(addresses[i]) == 'nan' else str(addresses[i]),
                        "warehoused": "yes" if warehoused[i]=="Тийм" else "no"  
                    }
                    accounts_to_add.append(accoount_dict)
                else:
                    continue

            try:
                hashed_password = bcrypt.generate_password_hash('password')
                for i, account_to_add in enumerate(accounts_to_add):
                    new_account = models.User()
                    new_account.company_name = account_to_add["company_name"].lower()
                    new_account.lastname = account_to_add["lastname"].capitalize()
                    new_account.firstname = account_to_add["firstname"].capitalize()
                    new_account.phone = account_to_add["phone"]
                    new_account.phone_extra = account_to_add["phone_extra"]
                    new_account.email = account_to_add["email"]
                    new_account.address = account_to_add["address"]
                    new_account.password = hashed_password
                    new_account.status='verified',
                    new_account.created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    new_account.modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),

                    if account_to_add["warehoused"] == "yes":
                        user_role = connection.query(models.Role).filter_by(name="supplier1").first()
                        new_account.roles.append(user_role)
                        connection.add(new_account)
                    elif account_to_add["warehoused"] == "no":
                        user_role = connection.query(models.Role).filter_by(name="supplier2").first()
                        new_account.roles.append(user_role)
                        connection.add(new_account)

                connection.commit()
            except Exception as e:
                flash(f'Алдаа гарлаа! {e}', 'danger')
                connection.rollback()
                return redirect(url_for('admin_account.accounts_from_excel'))
            else:
                flash('Данснууд нэмэгдлээ.', 'success')
                return redirect(url_for('admin_account.accounts_from_excel'))

    return render_template('/admin/account_from_excel.html', cur_date=cur_date, form=form, accounts_to_add=accounts_to_add)



@admin_account_blueprint.route('/admin/accounts/from-excel/products', methods=['GET', 'POST'])
@login_required
@has_role('admin')
def accounts_from_excel_products():

    cur_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")).date()
    form = CreateProductsFromExcelForm()
    products = []
    connection = Connection()
    suppliers = connection.query(models.User).outerjoin(models.Product,models.User.id==models.Product.supplier_id).filter(models.User.roles.any(models.Role.name=="supplier1"), models.Product.supplier_id == None).all()
    form.suppliers.choices = [(supplier.id, supplier.company_name) for supplier in suppliers]
    form.suppliers.choices.insert(0, (0,'Харилцагч сонгох'))
    
    if form.validate_on_submit():
        if len(request.files) > 0 and request.files['excel_file'].filename != "":
            excel_file = request.files['excel_file']
            df = pd.read_excel(excel_file)

            product_names = df['product name'].values
            colors = df['color'].values
            sizes = df['size'].values
            prices = df['price'].values
            product_types = df['product type'].values
            tailbars = df['tailbar'].values
            zaavars = df['zaavar'].values

            for i, product_name in enumerate(product_names):
                if (str(product_name) != 'nan'):
                    account_dict = {
                        "product_name": product_name,
                        "color": colors[i] if colors[i] != 'nan' else "Өнгөгүй",
                        "size": sizes[i] if sizes[i] != 'nan' else "Хэмжээгүй",
                        "product_type": product_types[i] if product_types[i] != 'nan' else "",
                        "price": prices[i] if prices[i] != 'nan' else "0",
                        "tailbar": tailbars[i] if tailbars[i] != 'nan' else "",
                        "zaavar": zaavars[i] if zaavars[i] != 'nan' else ""
                    }
                    products.append(account_dict)
                else:
                    continue

            try:
                product_supplier = connection.query(models.User).filter(models.User.id==form.suppliers.data).first()

                for i, product in enumerate(products):
                    product_count = connection.execute('select count(*) from sunsundatabase1.product as product where product.name = :product_name and product.color = :color_name and product.size = :size_name',{'product_name': product["product_name"], 'color_name': product["color"], 'size_name': product["size"]}).scalar()
                    if product_count > 1:
                        continue
                    else:
                        new_product = models.Product()
                        new_product.name = product["product_name"].lower()
                        new_product.price = int(product["price"])
                        new_product.product_type = product["product_type"]
                        new_product.description = product["tailbar"]
                        new_product.usage_guide = product["zaavar"]
                        new_product.color = product["color"]
                        new_product.size = product["size"]
                        new_product.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                        new_product.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar")),

                        product_supplier.products.append(new_product)
                        connection.flush()

                        total_inventory = models.TotalInventory()
                        total_inventory.quantity = 0
                        total_inventory.product_id = new_product.id
                        total_inventory.user_id = product_supplier.id
                        total_inventory.created_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        total_inventory.modified_date = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
                        connection.add(total_inventory)

                connection.commit()
            except Exception as e:
                flash(f'Алдаа гарлаа! {e}', 'danger')
                connection.rollback()
                return redirect(url_for('admin_account.accounts_from_excel_products'))
            else:
                flash('Бараанууд нэмэгдлээ.', 'success')
                return redirect(url_for('admin_account.accounts_from_excel_products'))

    return render_template('/admin/account_from_excel_products.html', cur_date=cur_date, form=form, products=products)