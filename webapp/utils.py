import uuid
import os
import io
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image
from flask import current_app
from wtforms.validators import ValidationError
from itsdangerous.url_safe import URLSafeTimedSerializer
from dateutil import tz
import jinja2
from datetime import datetime, time
import pytz


credentials = service_account.Credentials.from_service_account_file('webapp/servicekey.json')
client = storage.Client(project='sunsun-delivery', credentials=credentials)


def generate_uuid():
    return str(uuid.uuid4())


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            max_age=expiration
        )
    except:
        return False
    return email


def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def ImageFileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb*1024*1024
    def file_length_check(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(f"Зураг дээд хэмжээ {max_size_in_mb}MB байх ёстой!")
    return file_length_check


def add_and_resize_image(image_file):
    ext = image_file.filename.rsplit(".", 1)[1].lower()
    img_sizes = [(128,128),(300,300),(800,800)]
    uploadId= uuid.uuid4().hex

    if ext == 'png':
        image = Image.open(image_file)
        
        for size in img_sizes:
            thumbName = '%s_%s.jpg' % (uploadId, str('x'.join(tuple(map( str , size )))))
            image1 = image.resize((size), Image.ANTIALIAS)
            image1.save(fp=thumbName, format="PNG")
            client = storage.Client(project='sunsun-delivery', credentials=credentials)
            bucket = client.get_bucket('sunsun-general-bucket')
            blob = bucket.blob('{0}/'.format(uploadId) + '{0}'.format(thumbName))
            blob.upload_from_filename(thumbName, content_type='image/png')
            os.remove(thumbName)
        return uploadId
    else:
        image = Image.open(image_file)
        
        for size in img_sizes:
            image = Image.open(image_file)
            image_io = io.BytesIO()
            if image.width != image.height:
                image = crop_max_square(image).resize((size), Image.LANCZOS)
            image.thumbnail(size)
            image.save(image_io, "JPEG", quality=95)
            thumbName = '%s_%s.jpg' % (uploadId, str('x'.join(tuple(map( str , size )))))
            with open(thumbName, 'wb') as file_output:
                file_output.write(image_io.getvalue())
                file_output.close()
                client = storage.Client(project='sunsun-delivery', credentials=credentials)
                bucket = client.get_bucket('sunsun-general-bucket')
                blob = bucket.blob('{0}/'.format(uploadId) + '{0}'.format(thumbName))
                blob.upload_from_filename(thumbName, content_type='image/jpg')
                os.remove(thumbName)
        return uploadId


def add_image(image_file):
    ext = image_file.filename.rsplit(".", 1)[1].lower()
    uploadId= uuid.uuid4().hex

    if ext == 'png':
        image = Image.open(image_file)
        image.save(fp=uploadId, format="PNG")
        client = storage.Client(project='sunsun-delivery', credentials=credentials)
        bucket = client.get_bucket('sunsun-general-bucket')
        blob = bucket.blob(uploadId)
        blob.upload_from_filename(uploadId, content_type='image/png')
        os.remove(uploadId)
        return uploadId
    else:
        image = Image.open(image_file)
        image_io = io.BytesIO()
        image.save(image_io, "JPEG", quality=95)
        with open(uploadId, 'wb') as file_output:
            file_output.write(image_io.getvalue())
            file_output.close()
            client = storage.Client(project='sunsun-delivery', credentials=credentials)
            bucket = client.get_bucket('sunsun-general-bucket')
            blob = bucket.blob(uploadId)
            blob.upload_from_filename(uploadId, content_type='image/jpg')
            os.remove(uploadId)
        return uploadId


def datetimefilter(value):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = value.replace(tzinfo=from_zone)
    cur_date = utc.astimezone(to_zone)
    now = cur_date.strftime('%Y-%m-%d %H:%M:%S')
    return now


def datefilter(value):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = value.replace(tzinfo=from_zone)
    cur_date = utc.astimezone(to_zone)
    now = cur_date.strftime('%Y-%m-%d')
    return now


def numberformat(value):
    return format(int(value), ',d')


def checkdate(d1, d2):
    if time.mktime(time.strptime(d1, "%Y-%m-%d %H:%M:%S")) < time.mktime(time.strptime(d2,"%Y-%m-%d %H:%M:%S")):
        return True
    else:
        return False


def diffdates(d1, d2):
    return (time.mktime(time.strptime(d2,"%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(d1, "%Y-%m-%d %H:%M:%S")))


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now(pytz.timezone("Asia/Ulaanbaatar")).time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


FILTERS = [numberformat, datefilter, diffdates, checkdate]


def init_app(app):
    """Register the template filters with an app instance"""
    for func in FILTERS:
        app.add_template_filter(func)


