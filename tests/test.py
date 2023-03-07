# def test_supplier1_order_add(client, db_session, authenticated_supplier1):
#     # authenticated_supplier1 is a fixture that logs in a test supplier1 user

#     # Add a product
#     product = models.Product(name='Test product', price=10)
#     db_session.add(product)
#     db_session.commit()

#     # Add an inventory for the product
#     inventory = models.Inventory(product_id=product.id, quantity=100)
#     db_session.add(inventory)
#     db_session.commit()

#     response = client.get('/supplier1/orders/add')
#     assert response.status_code == 200

#     data = {
#         'district': 'Test district',
#         'khoroo': '1',
#         'aimag': 'Test aimag',
#         'phone': '12345678',
#         'phone_more': '12345679',
#         'address': 'Test address',
#         'product': [str(product.id)],
#         'quantity': ['10'],
#         'total_amount': '100',
#         'order_type': '0',
#     }

#     response = client.post('/supplier1/orders/add', data=data, follow_redirects=True)
#     assert response.status_code == 200
#     assert b'Хүргэлт нэмэгдлээ.' in response.data

#     # Check that the order was added to the database
#     order = db_session.query(models.Delivery).filter(models.Delivery.total_amount == 100).one_or_none()
#     assert order is not None

#     # Check that the order has the correct delivery date
#     now = datetime.now(pytz.timezone("Asia/Ulaanbaatar"))
#     delivery_date = now if is_time_between(time(6,30), time(10,30)) else now + timedelta(hours=+24)
#     assert order.delivery_date.replace(microsecond=0) == delivery_date.replace(microsecond=0)

#     # Check that the order has the correct address
#     assert order.addresses.district == 'Test district'
#     assert order.addresses.khoroo == '1'
#     assert order.addresses.aimag is None
#     assert order.addresses.address == 'Test address'
#     assert order.addresses.phone == '12345678'
#     assert order.addresses.phone_more == '12345679'

#     # Check that the order has the correct delivery details
#     order_detail = order.delivery_details[0]
#     assert order_detail.product_id == product.id
#     assert order_detail.quantity == 10

#     # Check that the inventory was updated correctly
#     inventory = db_session.query(models.Inventory).filter(models.Inventory.product_id == product.id).one()
#     assert inventory.quantity == 90