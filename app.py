# import os
# import sys
# from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
# import requests
# from flask_sqlalchemy import SQLAlchemy
#
#
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except ImportError as e:
#     pass
#
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#
# from mpg import Client
#
# app = Flask(__name__)
# print(os.environ)
# DEBUG = False
# TESTING = False
# CSRF_ENABLED = True
# SECRET_KEY = '2albekbahrmaleh'
# SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/flask_payment'
# db = SQLAlchemy(app)
#
# merchant_id = 'merchant.EGPTEST1'
# access_code = os.getenv('access_code')
# secret = os.getenv('secret')
# currency = 'ZMW'
# amount = 1
#
# client = Client(
#     merchant_id,
#     access_code,
#     secret,
#     currency,
#     receipt_url='http://127.0.0.1:8080/receipt'
# )
#
#
#
#
# class PaymentSessions(db.Model):

#
#
#

#
#
#

#
#
# @app.route('/paymentlink')

#
#
# @app.route('/return', methods=['POST'])
# def payment_link():
#     request_data = request.get_json()
#
#
#
#     # print(request_data)
#     # print(request_data['response']['session']['id'])
#     # return request_data
#     # language = request_data['language']
#     # framework = request_data['framework']
#
#     # two keys are needed because of the nested object
#
#
#
#
#
#
#     # link = client.payment_link(amount)
#     # # print(link)
#     #
#     # res = {
#     #     "res": "Generate 3 Party Link",
#     #     "payment_link": link
#     # }
#     #
#     # return jsonify(res)
#
#
# @app.route('/receipt')
# def receipt():
#
#     req_data = request.args
#
#     res_data = {
#         **req_data
#     }
#
#     res_data['txn_is_verified'] = client.verify_txn(res_data)
#
#     return jsonify(res_data)
#
#
# if __name__ == '__main__':
#     app.run(
#         host='0.0.0.0',
#         port=8080,
#         debug=True
#     )





# Previous imports remain...
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, request, render_template, redirect,session,url_for
import requests
from flask_user import login_required, UserManager, UserMixin
import cryptocode
import json
import random
from urllib.parse import quote, unquote


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://abanoub:.ABanob23@localhost:5432/flask_payment2"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-User settings
app.config['USER_APP_NAME'] = "Payment Service"  # Shown in and email templates and page footers
app.config['USER_ENABLE_EMAIL'] = False  # Disable email authentication
app.config['USER_ENABLE_USERNAME'] = True  # Enable username authentication
app.config['USER_REQUIRE_RETYPE_PASSWORD'] = False  # Simplify register form
app.config['SECRET_KEY'] = 'ksdfnjdfndjfbnsdjfbsdfsdfk5g5fg41f5g41fg5f4g5dfg415h4rhj4'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()`~-=_+[]{}|;\':",./<>? '
numbers = ['%02d' % i for i in range(100)]
random.shuffle(numbers)
# print(random.shuffle(numbers))
cypher = {a: b for a, b in zip(LETTERS, numbers)}

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')




CustomerSession = db.Table('customer_session',
                              db.Column('id',
                                        db.Integer,
                                        primary_key=True),
                              db.Column('customer_id',
                                        db.Integer,
                                        db.ForeignKey('customer.id', ondelete="cascade")),
                              db.Column('session_id',
                                        db.Integer,
                                        db.ForeignKey('payment_session.payment_id', ondelete="cascade")))



class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(140), index=True)
    mobile = db.Column(db.String(20))
    odoo_id = db.Column(db.Integer, unique=True)

    # transaction_id = db.Column(db.Integer, db.ForeignKey("payment_session.payment_id"))
    paymentsessions = db.relationship("PaymentSession",backref=db.backref('customer', lazy='joined'),
        lazy='dynamic')
    created_at = db.Column(db.DateTime, server_default=db.func.now())


    def __init__(self,name,mobile, odoo_id, transaction=[]):
        self.name = name
        self.mobile = mobile
        self.odoo_id = odoo_id
        self.transaction = transaction




    def __repr__(self):
        return f"<Customer {self.name}>"


class PaymentSession(db.Model):
    __tablename__ = 'payment_session'

    id = db.Column('payment_id', db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), index=True, unique=True)  # request_data['response']['session']['id']
    device = db.Column(db.String(255))  # request_data['response']['device']['browser']
    ipaddress = db.Column(db.String(255))  # request_data['response']['device']['ipAddress']
    operation = db.Column(db.String(255))  # request_data['response']['interaction']['operation']
    successindicator = db.Column(db.String(255),
                                 index=True)  # request_data['response']['interaction']['successIndicator']
    amount = db.Column(db.String(255))  # request_data['response']['order']['amount']
    certainty = db.Column(db.String(255))  # request_data['response']['order']['certainty']
    currency = db.Column(db.String(255))  # request_data['response']['order']['currency']
    reservation_refrence = db.Column(db.String(255))  # request_data['response']['order']['id']
    updatestatus = db.Column(db.String(255))  # request_data['response']['session']['updateStatus']
    card_brand = db.Column(db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['brand']
    expiary_year = db.Column(
        db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['expiry']['month']
    expiary_month = db.Column(
        db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['expiry']['year']
    fundingmethod = db.Column(
        db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['fundingMethod']
    nameoncard = db.Column(
        db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['nameOnCard']
    numberofcard = db.Column(db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['number']
    scheme = db.Column(db.String(255))  # request_data['response']['sourceOfFunds']['provided']['card']['scheme']
    status = db.Column(db.String(255), index=True)  # request_data['response']['status']
    transactionid = db.Column(db.String(255),
                              index=True)  # request_data['response']['transaction']['acquirer']['transactionId']
    created_at = db.Column(db.DateTime, server_default=db.func.now())


    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    # customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))



    def __init__(self,session_id,successindicator):
        self.session_id = session_id
        self.successindicator = successindicator


    def __repr__(self):
        return [self.session_id,]


user_manager = UserManager(app, db, User)



# @app.route('/')
# def home_page():
#         # String-based templates
#     return render_template_string("""
#             {% extends "flask_user_layout.html" %}
#             {% block content %}
#                 <h2>Home page</h2>
#                 <p><a href={{ url_for('user.register') }}>Register</a></p>
#                 <p><a href={{ url_for('user.login') }}>Sign in</a></p>
#                 <p><a href={{ url_for('home_page') }}>Home page</a> (accessible to anyone)</p>
#                 <p><a href={{ url_for('member_page') }}>Member page</a> (login required)</p>
#                 <p><a href={{ url_for('user.logout') }}>Sign out</a></p>
#             {% endblock %}
#         """)
@app.route('/')
def home():
    return render_template('error_page.html')

@app.route('/success', methods=['GET'])
def success_handler():
    print(session)
    # request_data = request.get_json()
    # if request.get_json() and request.method == 'POST':
    #     print('post',request_data)
    #     return render_template('success_payment.html')
    #
    # else:

    return render_template('success_payment.html',transaction=session['messages'])


@app.route('/error', methods=['GET'])
def error_handler():
    return render_template('error_page.html')

@app.route('/createlink', methods=['POST'])
def link_creator():
    request_data = request.get_json()
    print(request_data)
    # encoded = cryptocode.encrypt(str(request_data), ".ABanob23")



    x = ''.join(cypher[ch] for ch in str(request_data))


    return {'url':'http://127.0.0.1:5000/paymentlink/'+x+'/'}

@app.route('/paymentlink/<params>/', methods=['GET'])
def create_payment_link(params):
    # decoded = cryptocode.decrypt(params, ".ABanob23")
    # args = json.loads(decoded)
    inverse_cypher = {b: a for a, b in cypher.items()}
    n = ''.join(inverse_cypher[a + b] for a, b in zip(*[iter(params)] * 2))
    print(type(n))
    args = eval(n)
    if request.method == 'GET':
        if args:
            args['order_id']
            data = {'apiOperation': 'CREATE_CHECKOUT_SESSION',
                    'apiUsername': 'merchant.EGPTEST1',
                    'apiPassword': '61422445f6c0f954e24c7bd8216ceedf',
                    'merchant': 'EGPTEST1',
                    'order.id': args['order_id'],
                    'interaction.operation': 'PURCHASE',
                    'interaction.timeout': 1800,
                    'interaction.merchant.address.line1': '9 EL Shaheed Sayed Zakaria Sheraton Heliopolis',
                    'interaction.merchant.address.line2': 'Cairo,11111',
                    'interaction.merchant.logo': 'https://i.imgur.com/fEGr569.png',  # use baseurl
                    'interaction.merchant.name': 'Cairo Airport Travel',
                    'interaction.merchant.phone': '+219970',
                    'interaction.merchant.email': 'info@cairoairporttravel.com',
                    # 'interaction.timeoutUrl': 'http://127.0.0.1:5000/timeout/',  # use baseurl
                    'order.amount': args['amount'],
                    'order.currency': args['currency'],
                    'order.certainty': 'FINAL',
                    'shipping.method': 'NOT_SHIPPED',
                    'transaction.source': 'INTERNET',
                    'transaction.acquirer.transactionId': args['order_id'],
                    }
            response = requests.post('https://test-nbe.gateway.mastercard.com/api/nvp/version/59',
                                     data=data).content.decode("utf-8")
            response_dict = {k: v for k, v in (line.split("=") for line in response.split('&'))}
            print(response_dict)
            created_session = PaymentSession(session_id=response_dict['session.id'],successindicator=response_dict['successIndicator'])

            db.session.add(created_session)
            print('jnjnjnjnjnjjnnnnnnnnnnnnnnjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjnnn')
            customer_session = Customer.query.filter_by(odoo_id=args['odoo_id']).first()
            if customer_session:
                customer_session.paymentsessions.append(created_session)
                db.session.commit()

            else:
                created_customer = Customer(name=args['name'], mobile=args['mobile'],
                                            odoo_id=args['odoo_id'])
                created_customer.paymentsessions.append(created_session)
                db.session.add(created_customer)
                db.session.commit()
                print(created_customer, created_customer.id, type(created_customer.id))


            if args['lang'] == 'AR':
                return render_template('arabic_payment_page.html', marchant='EGPTEST1', session_id=response_dict['session.id'])
            if args['lang'] == 'EN':
                return render_template('english_payment_page.html', marchant='EGPTEST1', session_id=response_dict['session.id'])
        else:
            return render_template('error_page.html')



@app.route('/customers', methods=['GET'])
@login_required  # User must be authenticated
def all_customers():
    return render_template('get_all_customers.html', customers=Customer.query.all(), title="Show Customers")



@app.route('/customer/<int:id>', methods=['GET'])
@login_required  # User must be authenticated
def get_customer(id):
    return render_template('get_customer.html', customer=Customer.query.filter_by(id=id).first_or_404(), customer_transactions=PaymentSession.query.filter_by(customer_id=id).all(),title="Customer profile")



@app.route('/transaction/<int:id>', methods=['GET'])
@login_required  # User must be authenticated
def get_transaction(id):
    return render_template('get_transaction.html', transaction=PaymentSession.query.filter_by(id=id).first_or_404(),title="Transacton profile")



@app.route('/transactions', methods=['GET'])
@login_required  # User must be authenticated
def all_transactions():
    return render_template('get_all_transactions.html', transactions=PaymentSession.query.all(), title="Show transactions")





@app.route('/return', methods=['POST'])
def handling_response():
    request_data = request.get_json()
    print(request_data['response']['session']['id'])
    payment_session_return = PaymentSession.query.filter_by(successindicator=request_data['response']['interaction']['successIndicator'],session_id=request_data['response']['session']['id']).first_or_404()

    if payment_session_return:

        payment_session_return.device = request_data['response']['device']['browser']
        payment_session_return.ipaddress = request_data['response']['device']['ipAddress']
        payment_session_return.operation = request_data['response']['interaction']['operation']
        payment_session_return.successindicator = request_data['response']['interaction']['successIndicator']
        payment_session_return.amount = request_data['response']['order']['amount']
        payment_session_return.certainty = request_data['response']['order']['certainty']
        payment_session_return.currency = request_data['response']['order']['currency']
        payment_session_return.reservation_refrence = request_data['response']['order']['id']
        payment_session_return.updatestatus = request_data['response']['session']['updateStatus']
        payment_session_return.card_brand = request_data['response']['sourceOfFunds']['provided']['card']['brand']
        payment_session_return.expiary_year = request_data['response']['sourceOfFunds']['provided']['card']['expiry']['year']
        payment_session_return.expiary_month = request_data['response']['sourceOfFunds']['provided']['card']['expiry']['month']
        payment_session_return.fundingmethod = request_data['response']['sourceOfFunds']['provided']['card']['fundingMethod']
        payment_session_return.nameoncard = request_data['response']['sourceOfFunds']['provided']['card']['nameOnCard']
        payment_session_return.numberofcard = request_data['response']['sourceOfFunds']['provided']['card']['number']
        payment_session_return.scheme = request_data['response']['sourceOfFunds']['provided']['card']['scheme']
        payment_session_return.status = request_data['response']['status']
        payment_session_return.transactionid = request_data['response']['transaction']['acquirer']['transactionId']
        db.session.commit()
        print(request_data['response']['session']['id'])

        session['messages'] = request_data['response']['interaction']['successIndicator']
        return render_template('success_payment.html',transaction=request_data['response']['interaction']['successIndicator'])
        #very important
        #create the payment on odoo and try to get printed receipt from odoo too....

    else:
        return render_template('error_page.html')




if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
        )
    db.create_all()

