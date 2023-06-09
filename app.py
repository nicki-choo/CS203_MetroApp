from flask import Flask, request, render_template, redirect, flash, url_for
from flask_mail import Mail, Message
import sqlite3
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'your-secret-key'
mail = Mail(app)

load_dotenv()

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nickidummyacc@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
mail = Mail(app)


@app.route('/register', methods=['GET'])
def main():  # put application's code here
    return render_template('register.html')


@app.route('/top_up', methods=['GET'])
def top_up():
    return render_template('topUpCard.html')

@app.route('/view_data', methods=['GET'])
def view_data():
    conn = sqlite3.connect('users.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    return users



@app.route('/register', methods=['POST'])
def register_user():
    conn = sqlite3.connect('users.sqlite')
    cursor = conn.cursor()

    received_data_obj = request.form
    data_obj_to_save = dict(received_data_obj)

    data_model = {
        'username': data_obj_to_save['username'],
        'email': data_obj_to_save['email'],
        'password': data_obj_to_save['password']
    }

    sql_query = """INSERT INTO users (username, email, password) VALUES (?,?,?)"""
    cursor.execute(sql_query, (data_model['username'], data_model['email'], data_model['password']))

    conn.commit()

    # Send verification email
    send_verification_email(data_model['email'])

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
