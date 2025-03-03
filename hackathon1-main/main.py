from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from flask import request
import socket
import threading
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import datetime
from datetime import timedelta
from flask_login import login_user, logout_user, login_required, current_user, LoginManager, UserMixin
from flask import request, render_template, redirect, url_for, flash, send_from_directory
import hashlib
import os
import sys
import re
import time
from flask_mail import Mail, Message
import random
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_ipban import IpBan
from itsdangerous import URLSafeTimedSerializer
import configus
import uuid
jwt_instance = jwt
email_pattern = r"^[a-z0-9](\.?[a-z0-9]){5,}@g(oogle)?mail\.com$"
username_pattern = r"^[a-zA-Z0-9]{4,10}$"
confHost, confPort, confPassword, confDbname, confUser= configus.getConfig()
app = Flask(__name__)
app.secret_key = "a9f8c3d6b5e4f1a0"
secretballs = URLSafeTimedSerializer('a9f8c3d6b5e4f1a0')
mail = Mail(app)
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.login_message = "You need to login first."
login_manager.login_message_category = "info"
app.config['UPLOAD_FOLDER'] = 'C:/Server/funckenobispace/static'
app.config['RATELIMIT_STORAGE_URL'] = f"postgresql://postgres:111LZo0l4S7dzO0PXA3KOkasw2rcMtO46hY2FbUPxS@host:port/usersdb42"
app.config['MAIL_SERVER'] = 'funckenobi42.space'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USERNAME'] = 'support@funckenobi42.space'
app.config['MAIL_PASSWORD'] = '4242512'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
def get_real_ip():
    return request.access_route[0]

limiter = Limiter(
    get_real_ip,
    app=app,
    storage_uri="memory://",
    #on_breach=ban_ip
)

conn = psycopg2.connect(f"dbname={confDbname} user={confUser} password={confPassword} host={confHost} port={confPort}")

    # Create a cursor to execute queries
cur = conn.cursor()
# Create a LoginManager instance
login_manager = LoginManager()

# Initialize the login manager with the app
login_manager.init_app(app)

def get_file_size(file):
    if file.content_length:
        return file.content_length
    try:
        pos = file.tell()
        file.seek(0, 2) # seek to the end
        size = file.tell()
        file.seek(pos) # back to the original position
        return size
    except (AttributeError, IOError):
        return 0 # assume small enough

def connlog():
    if current_user.is_authenticated:
        print(f'[{datetime.datetime.now()}] A new {request.path} connection by [{current_user.username}]. [{request.method}]')
    else:
        print(f'[{datetime.datetime.now()}] A new {request.path} connection by {request.access_route[0]}. [{request.method}]')


def timeout_user():
    return 'You have been ratelimited.'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'webp', 'svg']
def allowed_file(filename): 
    extension = '.' in filename and filename.rsplit('.', 1)[1].lower()
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS, extension


@socketio.on('connect')
def handle_connect():
    print(f'[WebSocketIO][{request.remote_addr}] has connected to the radio socket.')

@socketio.on('message')
def handle_message(data):
    print(f'[WebSocketIO][{request.remote_addr}] Ping!: ' + data)

@socketio.on('disconnect')
def handle_disconnect():
    print(f'[WebSocketIO][{request.remote_addr}] disconnected')

# Define a User class that inherits from UserMixin and implements the required methods
class User(UserMixin):
    def __init__(self, id, username, email, password, role, picture):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.picture = picture

    # Define a method to get a user by id
    @staticmethod
    def get(user_id):
        # Query the database for the user with the given id
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        try:
            user = cur.fetchall()[0]
        except:
            return None
        # If the user exists, return a User object, otherwise return None
        if user:
            return User(user[0], user[1], user[2], user[3], user[4], user[7])
        else:
            return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
@limiter.limit("500 per hour",error_message='You have been ratelimited, and banned.')
def main():
    connlog()
    if current_user.is_authenticated:
        username = current_user.username
        if current_user.role == 'Admin':
            role = current_user.role
        else: 
            role = None
    else:
         username = 'Странник'
         role = None
    return render_template("index.html", user=username, role=role)

@app.route("/course_editor")
@limiter.limit("500 per hour",error_message='You have been ratelimited, and banned.')
def course_editor():
    connlog()
    course_id = request.args.get('course_id', default=None, type=str)
    if current_user.is_authenticated:
        username = current_user.username
        if current_user.role == 'Admin':
            role = current_user.role
        else: 
                flash('you are not an admin', 'error')
                return redirect(url_for("login"))
    else:
            flash('you are not an admin', 'error')
            return redirect(url_for("login"))
    return render_template("redactor.html", user=username, role=role, course_id=course_id)

@app.route("/<path:filename>")
def serve_google(filename):
    connlog()
    return send_from_directory("C:/Server/funckenobispace", filename)

@app.route("/static/<path:filename>")
def serve_static(filename):
    connlog()
    return send_from_directory("static", filename)

@app.route("/radio")
@login_required
def radio():
    connlog()
    if current_user.is_authenticated:
        username = current_user.username
    else:
         username = 'Странник'
    return render_template("radio.html", user=username)

@app.route("/queue")
@login_required
def queue():
    connlog()
    return render_template("queueIframe.html")


@app.route('/verification/<token>')
def verify(token):
    try:
        email = secretballs.loads(token, salt='email-confirm42', max_age=3600)
    except:
        flash('Confirmation link has expired, please contact the webmaster at contact@funckenobi42.space', 'error')
        return redirect(url_for("login"))
    cur.execute('UPDATE users SET confirmed = true WHERE email = %s', (email,))
    conn.commit()
    flash('Your account has been confirmed!', 'info')
    return redirect(url_for("login"))

# Define a route for the sign-up page
@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per day", methods=["POST"] ,error_message='You have been ratelimited for creating more than 10 accounts in a day.')
def register():
    connlog()
    # If the request method is GET, render the sign-up form
    if request.method == "GET":
        return render_template("register.html")
    # If the request method is POST, validate the user input and create a new user
    else:
        # Get the username and password from the form
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        # Check if the username and password are not empty
        if len(username) > 16:
            flash("Username maximum length is 16 characters. Try again.", 'error')
            return render_template("register.html")
        if username and email and password:
            password = password.encode()
            password = hashlib.sha256(password).hexdigest()
            # Check if the username already exists in the database
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchall()
            # If the username does not exist, insert a new user record into the database
            if not user:
                role = "User"
                cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)", (username, email, password, role))
                conn.commit()
                token = secretballs.dumps(email, salt='email-confirm42')
                confirm_url = url_for('verify', token=token, _external=True)
                subject = 'Please confirm your email'
                msg = Message(subject, sender='support@funckenobi42.space', recipients=[email])
                msg.body = f'To confirm your account, visit this page: \n {confirm_url} \n With respect, \n Prosto Patka Support'
                mail.send(msg)

                flash("A verification email has been sent to your mailbox.", 'info')
                return redirect(url_for("login"))
            # If the username already exists, flash an error message and render the sign-up form again
            else:
                flash("This username is already taken. Please choose a different one.", 'error')
                return render_template("register.html")
        # If the username or password is empty, flash an error message and render the sign-up form again
        else:
                flash("Please enter a valid username and password.", 'error')
                return render_template("register.html")


# Define a route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    connlog()
    # If the request method is GET, render the login form
    if request.method == "GET":
        return render_template("login.html")
    # If the request method is POST, authenticate the user credentials and log in the user
    else:
        # Get the username and password from the form
        email = request.form["email"]
        password = request.form["password"]
        # Check if the username and password are not empty
        if email and password:
            password = password.encode()
            password = hashlib.sha256(password).hexdigest()
            # Query the database for the user with the given username
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            try:
                user = cur.fetchall()[0]
            except:
                user = None
            # If the user exists and the password matches, log in the user using flask-login
            if user and user[3] == password:
                if user[6] == False:
                    flash("Please verify your account.")
                    return render_template("login.html")
                user = User(user[0], user[1], user[2], user[3], user[4], user[7])
                login_user(user)
                # Flash a success message and redirect to the profile page
                flash("You have successfully logged in." 'info')
                return redirect(url_for("main"))
            # If the user does not exist or the password does not match, flash an error message and render the login form again
            else:
                flash("Invalid username or password. Please try again.", 'error')
                return render_template("login.html")
        # If the username or password is empty, flash an error message and render the login form again
        else:
            if email and password:
                password = password.encode()
                password = hashlib.sha256(password).hexdigest()
                # Query the database for the user with the given username
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cur.fetchall()
                # If the user exists and the password matches, log in the user using flask-login
                if user and user[3] == password:
                    if user[6] == False:
                        flash("Please verify your account.")
                        return render_template("login.html")
                    user = User(user[0], user[1], user[2], user[3], user[4], user[7])
                    login_user(user)
                    # Flash a success message and redirect to the profile page
                    flash("You have successfully logged in.")
                    return redirect(url_for("profile"))
                # If the user does not exist or the password does not match, flash an error message and render the login form again
                else:
                    flash("Invalid username or password. Please try again.", 'error')
                    return render_template("login.html")
            flash("Please enter a valid username and password.", 'error')
            return render_template("login.html")

# Define a route for the logout page
@app.route("/logout")
@login_required
def logout():
    # Log out the user using flask-login
    logout_user()
    # Flash a success message and redirect to the home page
    flash("You have successfully logged out.")
    return redirect(url_for("main"))

# Define a route for the profile page
@app.route("/profile/<username>", methods=['GET', 'POST'])
@limiter.limit("10 per hour", methods=["POST"],error_message='You have been ratelimited for changing your profile picture more than 10 times in an hour.')
@login_required
def profile(username):
    connlog()
    if request.method == 'POST': 
        if 'uploaded-file' not in request.files: 
            flash('No file part', 'error')
            return redirect(request.url) 
        file = request.files['uploaded-file'] 
        size = get_file_size(file)
        if file.filename == '': 
            flash('No selected file', 'error') 
            return redirect(request.url) 
        if file and allowed_file(file.filename): 
            result, extension = allowed_file(file.filename)
            print(size)
            if size <= 20000:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                profileUser = cur.fetchone()
                filename = profileUser[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], (filename + '.' + extension))) 
                cur.execute('UPDATE users SET picture = %s WHERE username = %s', ((filename + '.' + extension), username,))
                conn.commit()
                flash('File uploaded successfully', 'info')
        else: 
            flash('ERROR 420. BALLS TOO BIG.', 'error')
    if username == current_user.username:
        return render_template("profile.html", username=current_user.username, email=current_user.email, picture=current_user.picture)

    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    try:
        profileUser = cur.fetchone()
    except:
        return render_template("profile.html", username='Unknown', email='Unknown')

    try:
        return render_template("profile.html", username=profileUser[1], email=profileUser[2], picture=profileUser[7])
    except:
        return render_template("profile.html", username='Unknown', email='Unknown', picture='balls')

@app.route("/checkout")
def checkout():
    connlog()
    product = request.args.get('product', default=None, type=str)
    if product == None:
        return redirect(url_for("login"))
    else:  
        cur.execute("SELECT * FROM Courses WHERE course_id = %s;", (product,))
        rows = cur.fetchall()
        htmlFile = ''
        for row in rows:
            name = row[2]
            photo = row[7]
            level = row[9]
            description = row[3]
            time = row[5]
            price = row[4]
            id = row[0]
            if price == 0:
                buttonText = "БЕСПЛАТНО!"
            else:
                buttonText = f"Купить за {price}руб"
            htmlFile = f"""
            <div class="col-md-5 col-lg-4 order-md-last">
            <h4 class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-primary">Ваша Корзина</span>
            <span class="badge bg-primary rounded-pill">3</span>
            </h4>
            <ul class="list-group mb-3">
            <li class="list-group-item d-flex justify-content-between lh-sm">
                <div>
                <h6 class="my-0">{name}</h6>
                <small class="text-muted">{description}</small>
                </div>
                <span class="text-muted">{price}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between bg-light">
                <div class="text-success">
                <h6 class="my-0">Промокод</h6>
                <small>НЕ ИНТЕГРИРОВАНО</small>
                </div>
                <span class="text-success">−$5</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                <span>Итого (RUB)</span>
                <strong>{price}</strong>
            </li>
            </ul>

            <form class="card p-2">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Promo code">
                <button type="submit" class="btn btn-secondary">Redeem</button>
            </div>
            </form>
        </div>
            """
            return render_template("checkout.html", product=htmlFile)

@app.route("/tos")
def tos():
    connlog()
    return render_template("tos.html")

@app.route("/about")
def about():
    connlog()
    return render_template("about.html")

@app.route("/create_course", methods=['GET', 'POST'])
def create_course():
        print(current_user.role)
        if current_user.role == "Admin":
            if request.method == 'POST':
                print('42')
                course_name = request.form["name"]
                course_desc = request.form["desc"]
                course_level = request.form["level"]
                course_time = request.form["time"]
                course_price = request.form["price"]
                course_photos = request.form["image"]
                cur.execute("SELECT course_id from Courses")
                print(cur.fetchall())
                if len(cur.fetchall()) == 0:
                    print('empty')
                    course_id = 0
                else:
                    course_id = int(cur.fetchall()[0]) + 1

                cur.execute("INSERT INTO Courses(title, description, duration, price, levls, category_id, photos) VALUES(%s,%s,%s,%s,%s,%s,%s)", (course_name, course_desc, course_time, course_price, course_level, 1, course_photos))
                conn.commit()
                cur.execute("SELECT * from Courses")
                print(cur.fetchall())
                return redirect(url_for('course_editor', course_id=course_id))
            else:
                return render_template("create_course.html")
        else:
            flash('Not an admin.', 'error')
            return redirect(url_for("login"))

@app.route("/courses")
def courses():
    cur.execute(
    "SELECT * FROM Courses;")
    rows = cur.fetchall()
    htmlFile = ''
    for row in rows:
        name = row[2]
        photo = row[8]
        level = row[3]
        description = row[4]
        time = row[7]
        price = row[6]
        id = row[0]
        if price == 0:
            buttonText = "БЕСПЛАТНО!"
        else:
            buttonText = f"Купить за {price}руб"
        htmlElement = f"""
            <div class="col">
                <div class="card shadow-sm">
                  <svg class="bd-placeholder-img card-img-top" width="100%" height="225" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="" preserveAspectRatio="xMidYMid slice" focusable="false"><title>Placeholder</title><rect width="100%" height="100%" fill="#55595c"></rect><text x="50%" y="50%" fill="#eceeef" dy=".3em"></text>
                    <title>Placeholder</title>
                    <image href="http://www.funckenobi42.space/static/{photo}" x="50%" y="50%" width="512" height="512" transform="translate(-256, -256)"/>
                  </svg>
                  <div class="card-body" style="text-align: left;">
                    <h2 class="card-text m-0">{name}</h2>
                    <h3 class="card-text m-0">{level}</h4>

                    <p class="card-text">{description}</p>
                    <div class="d-flex justify-content-between align-items-center text-align: right;">
                      <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-outline-secondary btn-warning"  onclick="window.location.href = '/courses/{id}$preview';">Предпросмотр</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary btn-success" onclick="window.location.href = '/checkout?product={id}';"> {buttonText} </button>

                      </div>
                      <small class="text-muted" style="font-size: 0.75rem;">Время: ~{time} мин</small>
                    </div>
                  </div>
                </div>
              </div>
        """
        print(row)
        htmlFile = htmlFile + htmlElement
        #    connlog()
    return render_template("courses.html", courses = htmlFile)
               
def ponger():
    #to keep alive connection if needed
    1

# t = threading.Thread(target=ponger, args=(), daemon=True)
# t.start()

if __name__ == "__main__":
    socketio.run(app, host='192.168.0.50', port=42125)
