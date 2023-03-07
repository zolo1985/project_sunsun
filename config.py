import os
import datetime
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

class Config(object):

    SERVER_NAME = os.environ.get("SERVER_NAME")
    SECRET_KEY=os.environ.get("SECRET_KEY")
    
    CACHE_TYPE = os.environ.get("CACHE_TYPE")
    CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_HOST")
    CACHE_REDIS_PORT = os.environ.get("CACHE_REDIS_PORT")
    CACHE_REDIS_DB = os.environ.get("CACHE_REDIS_DB")
    REDIS_URL = os.environ.get("REDIS_URL")

    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = False
    # USE BELOW CONFIG WITH HTTPS 
    SESSION_COOKIE_SECURE = False

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS')
    CORS_METHODS = os.environ.get('CORS_METHODS')
    CORS_SEND_WILDCARD = os.environ.get('CORS_SEND_WILDCARD')
    CORS_SUPPORTS_CREDENTIALS = os.environ.get('CORS_SUPPORTS_CREDENTIALS')

    MAIL_SERVER=os.environ.get('MAIL_SERVER')
    MAIL_PORT=os.environ.get('MAIL_PORT')
    MAIL_USE_TLS=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')

class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    
    DEBUG=False
    # SESSION_COOKIE_SECURE = True
    JWT_TOKEN_LOCATION = json.loads(os.environ["JWT_TOKEN_LOCATION"])
    JWT_COOKIE_SECURE = True
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=180)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=365)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = json.loads(os.environ["JWT_BLACKLIST_TOKEN_CHECKS"])

class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    
    DEBUG=True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    JWT_TOKEN_LOCATION = json.loads(os.environ["JWT_TOKEN_LOCATION"])
    JWT_COOKIE_SECURE = True
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=180)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=365)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = json.loads(os.environ["JWT_BLACKLIST_TOKEN_CHECKS"])