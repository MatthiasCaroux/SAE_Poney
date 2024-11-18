from app import app
from flask import render_template
from flask import request
from .models import User
from flask_login import login_user
from flask import flash, redirect, url_for


@app.route("/")
def home():
    return render_template("home.html")




@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Rechercher l'utilisateur dans la base de données
        user = User.query.filter_by(username=username).first()

        # Vérifier si l'utilisateur existe et si le mot de passe correspond
        if user and user.password == password:
            login_user(user)
            flash("Connexion réussie, bienvenue!", "success")
            return redirect(url_for('login'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    return render_template("login.html")
