from flask import Flask, request, render_template, redirect, flash, url_for, jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy, session
import os
from dotenv import load_dotenv

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
    

def validate_user_info(data):
    if 5 < len(data['username']) < 20:
        if '@' in data['email']:
            if len(data['password']) > 8:
                return jsonify({"Message": "User Added to Database"}), 201
            return jsonify({"Message": "Password Too Short"}), 400
        return jsonify({"Message": "Email Not Valid"}), 400
    return jsonify({"Message": "Username Needs to be between 5 - 20 characters"}), 400


def existing_usernames():
    db_users = User.query.all()
    usernames = []

    for user in db_users:
        usernames.append(user.username)

    return usernames


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

    if 'username' not in userdata or 'password' not in userdata or 'email' not in userdata:
        return jsonify({"message": "Necessary Info is missing"}), 400

    validate_user_info(userdata)

    new_user = User(
        username=userdata['username'],
        email=userdata['email'],
        password=userdata['password']
    )

    if userdata['username'] in existing_usernames():
        return jsonify({'error': 'Username is already in use'}), 400

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


@app.route('/fares')
def fares():
    return render_template('fares.html')


if __name__ == '__main__':
    app.run(debug=True)
