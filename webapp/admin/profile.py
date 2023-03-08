from flask import (Blueprint, render_template, flash, url_for, redirect)
from webapp import has_role, bcrypt
from flask_login import login_required
from .forms import PasswordChangeForm
from webapp.database import Connection
from flask_login import current_user
from webapp import models


admin_profile_blueprint = Blueprint('admin_profile', __name__)


@admin_profile_blueprint.route('/admin/profile', methods=['GET','POST'])
@login_required
@has_role('admin')
def profile():

    form = PasswordChangeForm()

    if form.validate_on_submit():
        connection = Connection()
        user = connection.query(models.User).get(current_user.id)

        if user.check_password(form.current_password.data):
            try:
                hashed_password = bcrypt.generate_password_hash(form.password.data)
                user.password = hashed_password
                connection.commit()
            except Exception as e:
                flash('Алдаа гарлаа!', 'danger')
                connection.rollback()
                return redirect(url_for('admin_profile.profile'))
            else:
                flash('Нууц үг амжилттай өөрчлөгдлөө', 'success')
                return redirect(url_for('admin_profile.profile'))
        else:
            flash('Одоо ашиглаж байгаа нууц үг буруу байна', 'danger')
            return redirect(url_for('admin_profile.profile'))

    return render_template('/shared/profile.html', form=form, current_user_id=current_user.id)