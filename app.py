from flask import Flask, request, render_template, redirect, flash, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'your-secret-key'

load_dotenv()

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
    users = db.relationship('User', backref='payment')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, tp_amount, cc_name, cc_number, cc_exp, cc_cvc, user_id):
        self.tp_amount = tp_amount
        self.cc_name = cc_name
        self.cc_number = cc_number
        self.cc_exp = cc_exp
        self.cc_cvc = cc_cvc
        self.user_id = user_id

@app.route('/register', methods=['GET'])
def register():  # put application's code here
    users = User.query.all()
    output = []

    for user in users:
        user_data = {
            'username': user.username,
            'email': user.email,
            'password': user.password
        }
        output.append(user_data)

    return render_template('register.html', users=output)


@app.route('/top_up', methods=['GET'])
def top_up():
    return render_template('topUpCard.html')


@app.route('/register', methods=['POST'])
def register_user():
    userdata = request.form

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
    flash('Registration successful! Please check your email for verification.')

    # Redirect to the login page
    return redirect(url_for('login'))


def send_verification_email(email):
    msg = Message("Welcome to MetroBus",
                  sender='nickidummyacc@gmail.com',
                  recipients=['270168718@yoobeestudent.ac.nz'])
    msg.body = 'Hello, your account has been registered successfully. Please verify your email.'
    mail.send(msg)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/fares')
def fares():
    return render_template('fares.html')


@app.route('/#')
def errPage():
    return render_template('err.html')


if __name__ == '__main__':
    app.run(debug=True)
