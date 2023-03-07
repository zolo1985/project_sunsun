from flask import (Blueprint, render_template, flash, redirect, url_for, abort, request)
from webapp import has_role
from flask_login import login_required
from webapp.database import Connection
from webapp import models
from datetime import datetime
from .forms import NewAccountForm, EditAccountForm, SelectAccountTypeForm
from webapp import bcrypt
import pytz

manager_account_blueprint = Blueprint('manager_account', __name__)

initial_roles = ['supplier1', 'supplier2', 'driver']

@manager_account_blueprint.route('/manager/accounts', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_accounts():
    connection = Connection()
    form = SelectAccountTypeForm()

    roles_selection = ['Жолооч', 'Харилцагч(агуулахтай)', 'Харилцагч(агуулахгүй)']
    form.accounts.choices = [role for role in roles_selection]
    
    if form.validate_on_submit():
        drivers = []
        supplier1s = []
        supplier2s = []
        if form.accounts.data == 'Жолооч':
            drivers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="driver")).all()
        elif form.accounts.data == 'Харилцагч(агуулахтай)':
            supplier1s = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).all()
        elif form.accounts.data == 'Харилцагч(агуулахгүй)':
            supplier2s = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier2")).all()
        
        return render_template('/manager/accounts.html', drivers=drivers, supplier1s=supplier1s, supplier2s=supplier2s, form=form)
    return render_template('/manager/accounts.html', drivers=[], supplier1s=[], supplier2s=[], form=form)



@manager_account_blueprint.route('/manager/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
@has_role('manager')
def manager_account(account_id):

    connection = Connection()
    account = connection.query(models.User).get(account_id)

    if account is None:
        flash('Олдсонгүй', 'danger')
        return redirect(url_for('manager_account.manager_accounts'))
        
    form = EditAccountForm()

    if form.validate_on_submit():
        account_to_update = connection.query(models.User).get(account_id)
        account_to_update.lastname = form.lastname.data.lower()
        account_to_update.firstname = form.firstname.data.lower()
        account_to_update.email = form.email.data
        account_to_update.phone = form.phone.data
        if account_to_update.has_role('driver'):
            account_to_update.delivery_rate = form.delivery_rate.data
        elif account_to_update.has_role('supplier1'):
            account_to_update.supplier_rate = form.supplier_rate.data
        elif account_to_update.has_role('supplier2'):
            account_to_update.supplier_rate = form.supplier_rate.data

        try:
            connection.commit()
        except:
            connection.rollback()
            flash('Алдаа гарлаа', 'danger')
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Мэдээлэл өөрчлөгдлөө', 'success')
            return redirect(url_for('manager_account.manager_accounts'))

    elif request.method == 'GET':
        form.lastname.data = account.lastname
        form.firstname.data = account.firstname
        form.email.data = account.email
        form.phone.data = account.phone
        if account.has_role('driver'):
            form.delivery_rate.data = account.delivery_rate
        else:
            form.supplier_rate.data = account.supplier_rate
        return render_template('/manager/edit_account.html', form=form, account=account)
    return render_template('/manager/edit_account.html', form=form, account=account)



@manager_account_blueprint.route('/manager/drivers/authorize/<int:driver_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_driver_authorize(driver_id):
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
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        abort(403)


@manager_account_blueprint.route('/manager/supplier1/authorize/<int:supplier1_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_supplier1_authorize(supplier1_id):
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
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        abort(403)



@manager_account_blueprint.route('/manager/supplier2/authorize/<int:supplier2_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_supplier2_authorize(supplier2_id):
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
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Жолоочийн төлөв өөрчлөгдлөө.', 'success')
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        abort(403)


@manager_account_blueprint.route('/manager/account/password-reset/<int:user_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_account_password_reset(user_id):
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
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            flash('Нууц үг password болж өөрчлөгдлөө.', 'success')
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        abort(403)


def switch_role(role):
    if role == "Харилцагч(агуулахтай)":
        return "supplier1"
    elif role == "Харилцагч(агуулахгүй)":
        return "supplier2"
    elif role == "Жолооч":
        return "driver"


@manager_account_blueprint.route('/manager/accounts/add-account', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_add_account():
    form = NewAccountForm()
    connection = Connection()
    roles_selection = ['Харилцагч(агуулахтай)', 'Харилцагч(агуулахгүй)', 'Жолооч']
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
            user.is_authorized = True
            connection.add(user)
            connection.commit()
        except Exception:
            flash('Алдаа гарлаа!', 'danger')
            connection.rollback()
            return redirect(url_for('manager_account.manager_add_account'))
        else:
            flash('Шинэ данс үүслээ баталгаажуулах и-мэйл илгээлээ.', 'success')
            return redirect(url_for('manager_account.manager_add_account'))

    return render_template('/manager/add_account.html', form=form)


@manager_account_blueprint.route('/manager/account/is-invoiced/<int:user_id>', methods=['GET','POST'])
@login_required
@has_role('manager')
def manager_account_is_invoiced(user_id):
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
            return redirect(url_for('manager_account.manager_accounts'))
        else:
            if user.is_invoiced:
                flash(f'%s нэхэмжилдэггүй боллоо.'%(user.company_name), 'success')
            else:
                flash(f'%s нэхэмжилдэг боллоо.'%(user.company_name), 'success')
            return redirect(url_for('manager_account.manager_accounts'))
    else:
        flash('Хэрэглэгч олдсонгүй!', 'danger')
        return redirect(url_for('manager_account.manager_accounts'))


