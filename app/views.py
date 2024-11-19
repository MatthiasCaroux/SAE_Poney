# from app import app
from flask import render_template, request
from app.models import *
from app import mysql, login_manager
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from flask import flash, redirect, url_for

userlog = False


@app.route("/")
def home():
    global userlog
    if current_user.is_authenticated:
        userlog = True
    return render_template("home.html", userlog = userlog)

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    cursor = mysql.connection.cursor()
    query = "SELECT username FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(username=user[0])
    return None

@app.route("/login/", methods=["GET", "POST"])
def login():
    global userlog
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        query = "SELECT username, password FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        print(user)
        cursor.close()

        if user and user[1] == password:
            login_user(User(username=user[0]))
            userlog = True
            return render_template("home.html", user = user, userlog = userlog)
        else:
            userlog = False
            error_message = "Nom d'utilisateur ou mot de passe incorrect"
            return render_template("login.html", error_message=error_message, user = user, userlog = userlog)
    return render_template("login.html", user = None, userlog = userlog)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    global userlog
    userlog = False
    return render_template("home.html", userlog = userlog)

@app.route("/poney")
def poney():
    return render_template("poney.html", poney=get_poney()[:10])