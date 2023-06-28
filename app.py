from flask import Flask, request, render_template, redirect, flash, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

from error import ERROR_EMAIL, ERROR_PASS, ERROR_USERNAME, ERROR_NAME_TAKEN, ERROR_MISSING_INFO

app = Flask(__name__)
app.secret_key = 'your-secret-key'
mail = Mail(app)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nickidummyacc@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False

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
    balance = db.Column(db.Float, primary_key=True)
    cc_name = db.Column(db.String(100), nullable=False)
    cc_number = db.Column(db.String(100), nullable=False)
    cc_exp = db.Column(db.String(100), nullable=False)
    cc_cvc = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='payment')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, balance, cc_name, cc_number, cc_exp, cc_cvc, user_id):
        self.balance = balance
        self.cc_name = cc_name
        self.cc_number = cc_number
        self.cc_exp = cc_exp
        self.cc_cvc = cc_cvc
        self.user_id = user_id
            
current_user = {
    'id': None,
    'username': None,
    'email': None
}
    
def validate_user_info(data):
    if 5 < len(data['username']) < 20:
        if '@' in data['email']:
            if len(data['password']) > 8:
                return True
            return ERROR_PASS.to_dict()
        return ERROR_EMAIL.to_dict()
    return ERROR_USERNAME.to_dict()


def existing_usernames():
    db_users = User.query.all()
    usernames = []

    for user in db_users:
        usernames.append(user.username)

    return usernames


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/top_up', methods=['POST', 'GET'])
def process_payment():
    if request.method == 'POST':
        payment_data = request.form

        new_payment = Payment(
            balance=payment_data['balance'],
            cc_name=payment_data['cc_name'],
            cc_number=payment_data['cc_number'],
            cc_exp=payment_data['cc_exp'],
            cc_cvc=payment_data['cc_cvc'],
            user_id=payment_data['user_id']
        )

        db.session.add(new_payment)
        db.session.commit()

        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        return render_template('topUpCard.html')
    else:
        return {"error": 'Method Not Allowed'}


@app.route('/register', methods=['POST'])
def register_user():
    userdata = request.form

    if 'username' not in userdata or 'password' not in userdata or 'email' not in userdata:
        return ERROR_MISSING_INFO.to_dict(), ERROR_MISSING_INFO.to_dict()['err_id']

    validation_result = validate_user_info(userdata)
    if validation_result != True:
        return validation_result, validation_result['err_id']

    if userdata['username'] in existing_usernames():
        return ERROR_NAME_TAKEN.to_dict(), ERROR_NAME_TAKEN.to_dict()['err_id']
 
    new_user = User(
        username=userdata['username'],
        email=userdata['email'],
        password=userdata['password']
    )
 
    db.session.add(new_user)
    db.session.commit()
 
    send_verification_email(userdata['email'])
    
    return redirect("login", code=201)


def send_verification_email(email):
    msg = Message("Welcome to MetroBus",
                  sender='nickidummyacc@gmail.com',
                  recipients=email)
    msg.body = 'Hello, your account has been registered successfully. Please verify your email. (This is also a test program for a university project)'
    mail.send(msg)


@app.route('/')
def dir_home():
    return redirect(url_for("home"))

@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_data = request.form
        user = User.query.filter_by(username=login_data['username']).first()
        print(user)
        
        current_user['id'] = user.id
        current_user['email'] = user.email
        current_user['username'] = user.username

        if user is None:
            print(False)
            return redirect(url_for('login'))
        else:
            if login_data['password'] != user.password:
                flash("Login information is incorrect", "warning")
                return redirect(url_for('login'))
            else:
                flash("Login Success!", "success")
                # Redirect to the profile route passing the logged-in username
                return redirect("/profile?username=" + user.username)

    elif request.method == 'GET':
        return render_template('login.html')
    else:
        return {"Request Error": "Invalid Request Method"}, 500


@app.route('/bus_fares', methods=['GET'])
def fares():
    return render_template('busfares.html')

@app.route('/profile', methods=['GET'])
def profile():
    if current_user['username'] != None:
        # Retrieve the username from the URL parameters
        username = current_user['username']

        # Retrieve the email from the user database
        user = User.query.filter_by(username=username).first()
        email = current_user['email']

        user_id = current_user['id']

        # Retrieve the balance from the payment database
        payment = Payment.query.filter_by(user_id=user.id).first()
        balance = payment.balance if payment else None

        # Set the default value for balance if it is None
        balance = balance if balance is not None else "00.00"

        return render_template('profile.html', username=username, email=email, user_id=user_id, balance=balance)


@app.route('/logout')
def logout():
    # The users non-sensitive info is stored in a dictionary defined at the top of the page and
    # used globally, so when they logout, all that does is remove all the info from the dictionary
    for i in current_user.keys():
        current_user[i] = None
        
    # Directing the user back to the home page after logout
    return redirect(url_for('home'), code=200)
    

if __name__ == '__main__':
    app.run(debug=True)
