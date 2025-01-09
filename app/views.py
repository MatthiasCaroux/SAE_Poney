# from app import app
from datetime import datetime
from flask import render_template, request
from app.models import *
from app import mysql, login_manager
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from flask import flash, redirect, url_for

@app.context_processor
def inject_userlog():
    return {"userlog": current_user.is_authenticated}

@app.route("/")
def home():
    return render_template("home.html")

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
            return redirect(url_for('home'))
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect"
            return render_template("login.html", error_message=error_message, user=user)
        
    return render_template("login.html", user=None)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "success")
    return redirect(url_for('home'))

@app.route("/profile/")
@login_required
def profile():
    cursor = mysql.connection.cursor()
    query = """
        SELECT * 
        FROM User 
        JOIN Adherent ON User.idConnexion = Adherent.idAdherent 
        WHERE User.Username = %s
    """
    cursor.execute(query, (current_user.username,))
    user = cursor.fetchone()
    cursor.close()
    return render_template("compte.html", user=user)


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.form.get('username')
        password = request.form.get('password')
        poids = request.form.get('poids')
        nom = request.form.get('nom')
        cotisation = request.form.get('cotisation') == '1'  # Checkbox
        telephone = request.form.get('telephone')

        # Vérifications des données
        if not username or not password or not nom or not poids or not telephone:
            error_message = "Tous les champs sont obligatoires."
            return render_template("register.html", error_message=error_message)

        if len(telephone) != 10 or not telephone.isdigit():
            error_message = "Le numéro de téléphone doit contenir 10 chiffres."
            return render_template("register.html", error_message=error_message)

        try:
            # Vérifier si l'utilisateur existe déjà
            cursor = mysql.connection.cursor()
            query_user_check = "SELECT Username FROM User WHERE Username = %s"
            cursor.execute(query_user_check, (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                error_message = "Ce nom d'utilisateur est déjà utilisé."
                return render_template("register.html", error_message=error_message)

            # Insérer dans la table Adherent
            query_adherent = """
                INSERT INTO Adherent (poids, nom, cotisation, Telephone)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_adherent, (poids, nom, cotisation, telephone))
            id_adherent = cursor.lastrowid

            # Insérer dans la table User en liant à l'adhérent
            query_user = """
                INSERT INTO User (Username, password, idConnexion)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_user, (username, password, id_adherent))

            # Commit de la transaction
            mysql.connection.commit()
            cursor.close()

            flash("Inscription réussie. Vous pouvez vous connecter.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            error_message = f"Une erreur s'est produite : {str(e)}"
            return render_template("register.html", error_message=error_message)

    return render_template("register.html")


@app.route("/poney")
def poney():
    return render_template("poney.html")


@app.route("/reservation/<id>")
def reservation(id):
    cours = get_cours_programme_by_id(id)
    listeponey = get_poney_dispo(id)
    return render_template("reservation.html", cours=cours, listeponey=listeponey, id = id)


@app.route("/planning")
def planning():
    current_week = datetime.now().isocalendar()[1]
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT *, DAYNAME(DateJour) AS Jour FROM CoursProgramme WHERE Semaine = %s", (current_week,))
    cours = cursor.fetchall()
    cursor.close()
    return render_template("planning.html", cours=cours)


@app.route("/adherer")
def adherer():
    return render_template("adherer.html")

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
            SELECT Adherent.idAdherent,Adherent.poids
            FROM User 
            NATURAL JOIN Adherent 
            WHERE User.username = %s AND User.idConnexion = Adherent.idAdherent
        """
        cursor.execute(query, (current_user.username,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            adherent_id = result[0]
            poids = result[1]
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


@app.route("/admin/")
@login_required
def admin():
    if current_user.username == 'admin':
        return render_template("admin.html")
    else:
        flash("Accès réservé à l'administrateur.", "danger")
        return redirect(url_for("home"))