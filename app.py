from flask import Flask, request, render_template, redirect, flash
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
    payment_id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float(0.00), nullable=False)
    cc_name = db.Column(db.String(100), nullable=False)
    cc_number = db.Column(db.String(100), nullable=False)
    cc_exp = db.Column(db.String(100), nullable=False)
    cc_cvc = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='payment', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, balance, cc_name, cc_number, cc_exp, cc_cvc, user_id):
        self.balance = balance
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
def register():  # put application's code here
    return render_template('register.html')


@app.route('/top_up', methods=['GET', 'POST'])
def top_up():
    user_id = request.args.get('user_id', default=None)
    # Retrieve the user object from the database
    user = User.query.get(user_id)

    if user_id is None or not user:
        flash("User not found", "error")
        return redirect("/top_up?user_id=" + str(user_id))

    if request.method == 'POST':
        # Process the payment transaction
        payment_data = request.form
        existing_payment = Payment.query.filter_by(user_id=user_id).first()

        if existing_payment:
            # Update existing payment data
            existing_payment.balance = payment_data['balance']
            existing_payment.cc_name = payment_data['cc_name']
            existing_payment.cc_number = payment_data['cc_number']
            existing_payment.cc_exp = payment_data['cc_exp']
            existing_payment.cc_cvc = payment_data['cc_cvc']

            # Calculate the top-up amount
            balance = float(payment_data.get('balance', 0))
            existing_payment.balance += balance
        else:
            # Create new payment data
            balance = float(payment_data.get('balance', 0))

            new_payment = Payment(
                balance=payment_data['balance'],
                cc_name=payment_data['cc_name'],
                cc_number=payment_data['cc_number'],
                cc_exp=payment_data['cc_exp'],
                cc_cvc=payment_data['cc_cvc'],
                user_id=user_id
            )
            db.session.add(new_payment)

        db.session.commit()

        # Redirect to the profile page after successful payment
        return redirect("/profile?user_id=" + str(user_id))

    return render_template('topUpCard.html', user_id=user_id, username=user.username)




# @app.route('/top_up', methods=['POST'])
# def process_payment():
#     payment_data = request.form
#     user_id = request.args.get('user_id', default=None)
#
#
#     new_payment = Payment(
#         balance=payment_data['balance'],
#         cc_name=payment_data['cc_name'],
#         cc_number=payment_data['cc_number'],
#         cc_exp=payment_data['cc_exp'],
#         cc_cvc=payment_data['cc_cvc'],
#         user_id=user_id
#     )
#     db.session.add(new_payment)
#     db.session.commit()
#
#     return render_template('topUpCard.html')



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
 
    # Send verification email
    #send_verification_email(userdata['email'])

    # Redirect to the login page
    return redirect("login", code=201)


def send_verification_email(email):
    msg = Message("Welcome to MetroBus",
                  sender='nickidummyacc@gmail.com',
                  recipients=email)
    msg.body = 'Hello, your account has been registered successfully. Please verify your email.'
    mail.send(msg)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_data = request.form

        user = User.query.filter_by(username=login_data['username']).first()

        if user is None:
            flash("User does not exist!", "danger")
            return redirect('/login')
        else:
            if login_data['password'] != user.password:
                flash("Login information is incorrect", "warning")
                return redirect('/login')
            else:
                flash("Login Success!", "success")
                # Redirect to the profile route passing the logged-in username
                return redirect("/profile?username=" + user.username)

    else:
        return render_template('login.html')


@app.route('/bus_fares', methods=['GET'])
def fares():
    return render_template('busfares.html')

@app.route('/profile', methods=['GET'])
def profile():
    # Retrieve the username from the URL parameters
    username = request.args.get('username')
    user_id = request.args.get('user_id')

    # Retrieve the email from the user database
    user = User.query.filter_by(username=username).first()
    email = user.email if user else None

    user_id = user.id if user else None

    # Retrieve the balance from the payment database
    payment = Payment.query.filter_by(user_id=user_id).first()
    balance = payment.balance if payment else None

    # Set the default value for balance if it is None
    balance = balance if balance is not None else "00.00"

    return render_template('profile.html', username=username, email=email, user_id=user_id, balance=balance)



if __name__ == '__main__':
    app.run(debug=True)
