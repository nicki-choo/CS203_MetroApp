from flask import Flask, request, render_template, redirect, flash, url_for, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy, session
import os
from dotenv import load_dotenv
from error import ERROR_EMAIL, ERROR_PASS, ERROR_USERNAME, ERROR_NAME_TAKEN, ERROR_MISSING_INFO
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.secret_key = 'your-secret-key'

load_dotenv()

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Metro App Revamp"
    }
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nickidummyacc@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
mail = Mail(app)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Payment(db.Model):
    __tablename__ = 'payment'
    tp_amount = db.Column(db.Float, primary_key=True)
    cc_name = db.Column(db.String(100), nullable=False)
    cc_number = db.Column(db.String(100), nullable=False)
    cc_exp = db.Column(db.String(100), nullable=False)
    cc_cvc = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('User', backref='payment')


    def __init__(self, tp_amount, cc_name, cc_number, cc_exp, cc_cvc, user_id):
        self.tp_amount = tp_amount
        self.cc_name = cc_name
        self.cc_number = cc_number
        self.cc_exp = cc_exp
        self.cc_cvc = cc_cvc
        self.user_id = user_id
    

def validate_user_info(data):
    if 5 < len(data['username']) < 20:
        if '@' in data['email']:
            if len(data['password']) > 8:
                return True
            return ERROR_PASS
        return ERROR_EMAIL
    return ERROR_USERNAME


def existing_usernames():
    db_users = User.query.all()
    usernames = []

    for user in db_users:
        usernames.append(user.username)

    return usernames

def existing_payments():
    db_payments = Payment.query.all()
    payments = []

    for payment in db_payments:
        payments.append(payment.tp_amount)

    return payments

@app.route('/register', methods=['GET'])
def register():  # put application's code here
    users = existing_usernames()
    return render_template('register.html', users=users)


@app.route('/top_up', methods=['GET'])
def top_up():
    payments = existing_payments()
    return render_template('topUpCard.html', payments=payments)

@app.route('/top_up', methods=['POST'])
def process_top_up():
    user_payment = request.form

    new_payment = Payment(
        tp_amount=user_payment['tp_amount'],
        cc_name=user_payment['cc_name'],
        cc_number=user_payment['cc_number'],
        cc_exp=user_payment['cc_exp'],
        cc_cvc=user_payment['cc_cvc'],
        user_id=user_payment['user_id']
    )

    db.session.add(new_payment)
    db.session.commit()

    return render_template('topUpCard.html')


@app.route('/register', methods=['POST'])
def register_user():
    userdata = request.form

    if 'username' not in userdata or 'password' not in userdata or 'email' not in userdata:
        return ERROR_MISSING_INFO
    
    if userdata['username'] in existing_usernames():
        return ERROR_NAME_TAKEN

    if validate_user_info(userdata):

        new_user = User(
            username=userdata['username'],
            email=userdata['email'],
            password=userdata['password']
        )

        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        send_verification_email(userdata['email'])

        # Show flash message after successful registration

        # Redirect to the login page
        return redirect('/login')
    
    else:
        return validate_user_info(userdata), 400


def send_verification_email(email):
    msg = Message("Welcome to MetroBus",
                  sender='nickidummyacc@gmail.com',
                  recipients=['270168718@yoobeestudent.ac.nz'])
    msg.body = 'Hello, your account has been registered successfully. Please verify your email.'
    mail.send(msg)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_data = request.form
        username_data = db.execute("SELECT username FROM users WHERE username=:username", {"username":login_data['username']}).fetchone()
        password_data = db.execute("SELECT password FROM users WHERE username=:username", {"username":login_data['username']}).fetchone()
        
        if username_data is None:
            flash("User does not exist!", "danger")
            return redirect('/login')
        else:
            if login_data['password'] != password_data:
                flash("Login information is incorrect", "warning")
                return redirect('/login')
            else:
                flash("Login Success!", "success")
                return redirect('/')
        
    else:
        return render_template('login.html')


@app.route('/bus_fares', methods=['GET'])
def bus_fares():
    return render_template('busfares.html')


app.register_blueprint(swagger_blueprint)


if __name__ == '__main__':
    app.run(debug=True)
