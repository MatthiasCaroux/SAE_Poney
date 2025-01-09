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
        cursor.close()

        if user and user[1] == password:
            login_user(User(username=user[0]))
            userlog = True
            return redirect(url_for('home'))
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
    return redirect(url_for('home'))

@app.route("/profile/")
@login_required
def profile():
    global userlog
    print(current_user.username)
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM User  natural join Adherent WHERE User.username = %s and User.idConnexion = Adherent.idAdherent"
    cursor.execute(query, (current_user.username,))
    user = cursor.fetchone()
    cursor.close()
    
    userlog = True
    return render_template("compte.html", user = user, userlog = userlog)

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        poids = request.form['poids']
        nom = request.form['nom']
        cotisation = request.form['cotisation']
        telephone = request.form['telephone']
        
        cursor = mysql.connection.cursor()
        query = "SELECT username FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            error_message = "Ce nom d'utilisateur est déjà utilisé"
            return render_template("register.html", error_message=error_message, user = user)

        query = "INSERT INTO User (username, password) VALUES (%s, %s)"
        query2 = "INSERT INTO Adherent (poids, nom, cotisation, telephone) VALUES (%s, %s, %s, %s)"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (username, password))
        cursor.execute(query2, (poids, nom, cotisation, telephone))
        mysql.connection.commit()
        cursor.close()
        return render_template("register.html", user = user)
    return render_template("register.html")

@app.route("/poney")
def poney():
    return render_template("poney.html")#ajouter les poneys


@app.route("/reservation/<id>")
def reservation(id):
    cours = get_cours_programme_by_id(id)
    listeponey = get_poney_dispo(id)
    return render_template("reservation.html", cours=cours, listeponey=listeponey, id = id)


@app.route("/planning")
def planning():
    return render_template("planning.html")


@app.route("/adherer")
def adherer():
    return render_template("adherer.html")
@app.route("/detail_cours/<id>")    
def detail_cours(id):
    cours = get_cours_programme_by_id(id)
    return render_template("detail_cours.html", cours=cours)

@app.route("/insert_reserver/<id>", methods=["GET", "POST"])
@login_required
def insert_reserver(id):
    if request.method == "POST":

        poney_id = request.form.get("poney")  
        if not poney_id:
            return redirect(url_for('reservation', id=id))  

        adherent_id = None
        cursor = mysql.connection.cursor()
        query = """
            SELECT Adherent.idAdherent
            FROM User 
            NATURAL JOIN Adherent 
            WHERE User.username = %s AND User.idConnexion = Adherent.idAdherent
        """
        cursor.execute(query, (current_user.username,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            adherent_id = result[0]
        else:
            return redirect(url_for('reservation', id=id))

        # Insérer la réservation
        try:
            print(id, adherent_id, poney_id)
            cursor = mysql.connection.cursor()
            query_insert = """
                INSERT INTO Reserver (idCoursRealise, idAdherent, idPoney)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_insert, (id, adherent_id, poney_id))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('profile'))  
        except Exception as e:
            return redirect(url_for('reservation', id=id))
    return redirect(url_for('home'))
