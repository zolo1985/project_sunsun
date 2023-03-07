from flask import (Blueprint, render_template)

main_blueprint = Blueprint('main', __name__,)

@main_blueprint.route('/')
def home():
    return render_template('/main/home.html', title='Үндсэн')

@main_blueprint.route('/about-us')
def about_us():
    return render_template('/main/about_us.html', title='Бидний тухай')

@main_blueprint.route('/delivery-zones')
def delivery_zones():
    return render_template('/main/zone.html', title='Бүсүүд')

@main_blueprint.route('/activity')
def activity():
    return render_template('/main/activity.html', title='Үйл ажиллагаа')

@main_blueprint.route('/jobs')
def jobs():
    return render_template('/main/jobs.html', title='Ажлын байр')

@main_blueprint.route('/customer-feedback')
def customer_feedback():
    return render_template('/main/reviews.html', title='Харилцагчийн сэтгэгдэл')

@main_blueprint.route('/contact-us')
def contact_us():
    return render_template('/main/contact_us.html', title='Холбоо барих')

@main_blueprint.route('/privacy')
def privacy():
    return render_template('/main/privacy.html', title='Хувийн мэдээлэл')

@main_blueprint.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('/main/terms_and_conditions.html', title='Хэрэглэх Журам ба Үйлчилгээний Нөхцөл')