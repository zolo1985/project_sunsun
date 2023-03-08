from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from webapp.auth.forms import SignInForm, RequestResetForm, ResetPasswordForm
from webapp.database import Connection
from webapp import models
from webapp.utils import generate_confirmation_token, confirm_token
from webapp import bcrypt
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/signin', methods=['GET','POST'])
def signin():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SignInForm()

    if form.validate_on_submit():
        connection = Connection()
        user = connection.query(models.User).filter_by(email=form.email.data).first()
        if user:
                if user.status == "unverified" and user.check_password(form.password.data):
                    flash('Таны данс баталгаажаагүй байна! Та менежертэй холбогдоно уу!', 'info')
                    return render_template('/auth/signin.html', form=form, title='Нэвтрэх')
                elif user.is_authorized == False and user.check_password(form.password.data):
                    flash('Таны данс хаагдсан байна. Менежертэй холбогдоно уу!', 'info')
                    return render_template('/auth/signin.html', form=form, title='Нэвтрэх')
                else:
                    if user.check_password(form.password.data):
                        login_user(user)
                        flash(f"Сайна байна уу %s!"%(user.firstname), category="success")
                        if user.has_role('supplier1'):
                            return redirect(url_for('supplier1_dashboard.supplier1_dashboard'))
                        elif user.has_role('supplier2'):
                            return redirect(url_for('supplier2_dashboard.supplier2_dashboard'))
                        elif user.has_role('manager'):
                            return redirect(url_for('manager_dashboard.manager_dashboard'))
                        elif user.has_role('clerk'):
                            return redirect(url_for('clerk_dashboard.clerk_dashboard'))
                        # elif user.roles[0] == "admin":
                        #     return redirect(url_for('main.home'))
                        elif user.has_role('accountant'):
                            return redirect(url_for('accountant_dashboard.accountant_dashboard'))
                        elif user.has_role('driver'):
                            return redirect(url_for('driver_order.driver_orders'))
                        else:
                            return redirect(url_for('main.home'))
                    else:
                        flash('Хэрэглэгч олдсонгүй!', 'danger')
                        return render_template('/auth/signin.html', form=form, title='Нэвтрэх')
        else:
            flash('Хэрэглэгч олдсонгүй!', 'danger')
            return render_template('/auth/signin.html', form=form, title='Нэвтрэх')

    return render_template('/auth/signin.html', form=form, title='Нэвтрэх')


@auth_blueprint.route('/signout', methods=['GET','POST'])   
@login_required
def signout():
    logout_user()
    return redirect(url_for('main.home'))



@auth_blueprint.route("/reset-password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        connection = Connection()
        user = connection.query(models.User).filter_by(email=form.email.data).first()
        connection.close()

        if user:
            token = generate_confirmation_token(user.email)
            try:
                sender_email = "sunsundelivery247@gmail.com"
                receiver_email = user.email
                password = "nutahfravahagmph"
                message = MIMEMultipart("alternative")
                subject = "Нууц үг сэргээх"
                text = f'''Нууц үг сэргээх
                Линк нь дээр дарж нууц үгээ өөрчилнө үү! %s'''%(url_for('auth.reset_password', token=token, _external=True))
                part1 = MIMEText(text, "plain")
                message["Subject"] = subject
                message.attach(part1)

                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, receiver_email, message.as_string()
                    )

            except Exception as e:
                flash('Алдаа гарлаа! Та түр хүлээгээд дахин оролдоно уу!', 'danger')
            else:
                flash('Нууц үгээ өөрчлөх линк таны имэйл хаягруу илгээлээ.', 'info')
                return redirect(url_for('auth.signin'))
        else:
            flash('Нууц үгээ өөрчлөх линк таны имэйл хаягруу илгээлээ.', 'info')
            return redirect(url_for('auth.signin'))
    return render_template('/auth/reset_request.html', title='Нууц үг өөрчлөх', form=form)

@auth_blueprint.route("/reset-password/<string:token>", methods=['GET', 'POST'])
def reset_password(token):

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user_email = confirm_token(token)

    if user_email is None:
        flash('Нууц үг өөрчлөх цонх хаагдсан байна! та дахин хүсэлт илгээнэ үү!', 'warning')
        return redirect(url_for('auth.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            connection = Connection()
            user = connection.query(models.User).filter_by(email=user_email).first()
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            user.password = hashed_password
            connection.commit()
        except Exception:
            flash('Бүртгэл хийхэд алдаа гарлаа! Та түр хугацааны дараа дахин оролдоно уу!')
            connection.rollback()
        else:
            flash(f'Нууц үг амжилттай өөрчлөгдлөө.!', 'success')
            return redirect(url_for('auth.signin'))
    return render_template('/auth/reset_password.html', title='Нууц үг өөрчлөх', form=form)

