import logging
from datetime import datetime
import pytz
import random
import click
from faker import Faker
from webapp import bcrypt
from webapp.database import Connection
from webapp.models import (Role, User, Product)
from webapp import models
from sqlalchemy import or_

log = logging.getLogger(__name__)

faker = Faker()

initial_roles = ['supplier1', 'supplier2', 'manager', 'admin', 'driver', 'accountant', 'clerk']
initial_delivery_regions = ['Хойд', 'Урд', 'Зүүн', 'Баруун', 'Баруун Хойд', 'Зүүн Хойд', 'Баруун Урд', 'Зүүн Урд']
initial_districts = ['Багануур', 'Багахангай', 'Баянгол', 'Баянзүрх', 'Налайх', 'Хан-Уул', 'Сүхбаатар', 'Сонгинохайрхан', 'Чингэлтэй']
initial_aimags = ['Архангай','Баян-Өлгий','Баянхонгор','Булган','Говь-Алтай','Говьсүмбэр','Дархан-Уул','Дорноговь','Дорнод','Дундговь','Завхан','Орхон','Өвөрхангай','Өмнөговь','Сүхбаатар','Сэлэнгэ','Төв','Увс','Ховд','Хөвсгөл','Хэнтий']

def generate_roles():
    roles = list()
    connection = Connection()
    for rolename in initial_roles:
        role = connection.query(Role).filter_by(name=rolename).first()
        if role:
            roles.append(role)
            continue
        role = Role(name=rolename)
        roles.append(role)
        connection.add(role)
        try:
            connection.commit()
            connection.close()
        except Exception as e:
            log.error("Erro inserting role: %s, %s" % (str(role), e))
            connection.rollback()
            connection.close()
    return roles

def generate_accounts(n):
    connection = Connection()

    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='company%s'%(i), 
                    firstname='Төрөө%s'%(i),
                    lastname='Төрөө%s'%(i),
                    email='company%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="supplier1").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()

    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='supplier2%s'%(i), 
                    firstname='Галаа1%s'%(i),
                    lastname='Галаа1%s'%(i), 
                    email='supplier2%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="supplier2").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()


def generate_managers(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='sunsun%s'%(i), 
                    firstname='Баясаа%s'%(i),
                    lastname='Баясаа%s'%(i),
                    email='manager%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="manager").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()


def generate_accountants(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='accountant%s'%(i), 
            firstname='Өлзий%s'%(i),
            lastname='Өлзий%s'%(i),
            email='accountant%s@sunsun.com'%(i), 
            phone=faker.phone_number(),
            status='verified',
            created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
            modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
            password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="accountant").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()


def generate_clerks(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='clerk%s'%(i),
                    firstname='Сараа%s'%(i),
                    lastname='Сараа%s'%(i),
                    email='clerk%s@sunsun.com'%(i),
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="clerk").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()


def generate_admin():
    connection = Connection()
    hashed_password = bcrypt.generate_password_hash('password')
    user = User(company_name='sunsun',
                firstname='СҮН СҮН',
                lastname='СҮН СҮН',
                email='admin@sunsun.com',
                phone=faker.phone_number(),
                status='verified',
                created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                password=hashed_password)
        
    user_role = connection.query(Role).filter_by(name="admin").first()
    user.roles.append(user_role)
    connection.add(user)

    try:
        connection.commit()
    except Exception as e:
        connection.rollback()
        connection.close()
    else:
        connection.close()


def generate_drivers(n):
    connection = Connection()
    for i in range(n):
        hashed_password = bcrypt.generate_password_hash('password')
        user = User(company_name='driver%s'%(i), 
                    firstname='Галаа%s'%(i),
                    lastname='Галаа%s'%(i), 
                    email='driver%s@sunsun.com'%(i), 
                    phone=faker.phone_number(),
                    status='verified',
                    created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                    password=hashed_password)
            
        user_role = connection.query(Role).filter_by(name="driver").first()
        user.roles.append(user_role)
        connection.add(user)
        connection.commit()
        connection.close()

def generate_supplier1_products():
    connection = Connection()
    suppliers = connection.query(models.User).filter(models.User.roles.any(models.Role.name=="supplier1")).all()

    for i, supplier in enumerate(suppliers):
        for i in range(20):
            product = Product(
                name = faker.word(),
                price = random.randint(1000,10000),
                type = faker.word(),
                color = faker.color(),
                size = faker.color(),
                description = "Product description",
                usage_guide = "Use it for testing",
                created_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                modified_date=datetime.now(pytz.timezone("Asia/Ulaanbaatar")),
                image_url = "645e31ac9c60438c9224943d766fc41b"
            )
            supplier.products.append(product)
            connection.flush()

            inventory = models.Inventory()
            inventory.status = False
            inventory.product_id = product.id
            inventory.supplier_id = supplier.id

            connection.add(inventory)
            connection.commit()

    
def reset_database_data():
    connection = Connection()
    connection.execute("DROP DATABASE sunsundatabase1")
    connection.execute("CREATE DATABASE sunsundatabase1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    connection.close()

def register(app):
    @app.cli.command('test-data')
    def test_data():
        generate_roles()
        generate_admin()
        generate_clerks(2)
        generate_managers(2)
        generate_drivers(10)
        generate_accounts(10)
        generate_accountants(2)
        generate_supplier1_products()

    @app.cli.command('initial-data')
    def initial_data():
        generate_roles()
        generate_admin()

    @app.cli.command('test-suppliers')
    def test_suppliers():
        generate_accounts(10)
        generate_supplier1_products()

    @app.cli.command('reset-data')
    def reset_data():
        reset_database_data()

    @app.cli.command('gen-admin')
    def gen_admin():
        generate_admin()

    @app.cli.command('create-admin')
    @click.argument('company_name')
    @click.argument('firstname')
    @click.argument('lastname')
    @click.argument('password')
    def create_admin(company_name, firstname, lastname, email, password):
        connection = Connection()
        admin_role = connection.query(models.Role).filter(models.Role.name=="admin").first()
        user = User()
        user.company_name = company_name
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.set_password(password)
        user.roles.append(admin_role)
        try:
            connection.add(user)
            connection.commit()
            click.echo('User {0} Added.'.format(firstname))
        except Exception as e:
            log.error("Fail to add new user: %s Error: %s" % (firstname, e))
            connection.rollback()

    @app.cli.command('list-users')
    def list_users():
        try:
            connection = Connection()
            users = connection.query(models.User).all()
            for user in users:
                click.echo('{0}'.format(user.firstname))
        except Exception as e:
            log.error("Fail to list users Error: %s" % e)
            connection.rollback()

    @app.cli.command('list-routes')
    def list_routes():
        for url in app.url_map.iter_rules():
            click.echo("%s %s %s" % (url.rule, url.methods, url.endpoint))