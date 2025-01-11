# from app import app
from datetime import datetime
from hashlib import sha256
from flask import render_template, request
from app.models import *
from app import mysql, login_manager
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from flask import flash, redirect, url_for

@app.context_processor
def inject_userlog():
    if current_user.is_authenticated:
        return {"userlog": current_user.is_authenticated, "role": getattr(current_user, "role", None)}
    else:
        return {"userlog": False, "role": None}



@app.route("/")
def home():
    return render_template("home.html")

class User(UserMixin):
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    cursor = mysql.connection.cursor()
    query = "SELECT username, role FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(username=user[0], role=user[1])  # Charger le rôle avec l'utilisateur
    return None


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        query = "SELECT username, password, role FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[1] == password:
            login_user(User(username=user[0], role=user[2]))
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
        SELECT role
        FROM User 
        WHERE username = %s
    """
    cursor.execute(query, (current_user.username,))
    role = cursor.fetchone()[0]
    cursor.close()

    user = None
    if role == 'moniteur':  # Si l'utilisateur est un moniteur
        cursor = mysql.connection.cursor()
        query = """
            SELECT User.role, User.username, Moniteur.nom, Moniteur.prenom
            FROM Moniteur
            LEFT JOIN User ON Moniteur.nom = User.nom AND Moniteur.prenom = User.prenom 
            WHERE User.username = %s
        """
        cursor.execute(query, (current_user.username,))
        user = cursor.fetchone()
        cursor.close()
    elif role == 'adherent':  # Si l'utilisateur est un adhérent
        cursor = mysql.connection.cursor()
        query = """
            SELECT User.role, User.username, Adherent.nom, Adherent.prenom, Adherent.poids, Adherent.telephone, Adherent.cotisation
            FROM Adherent 
            LEFT JOIN User ON Adherent.nom = User.nom AND Adherent.prenom = User.prenom
            WHERE User.username = %s
        """
        cursor.execute(query, (current_user.username,))
        user = cursor.fetchone()
        cursor.close()

    return render_template("compte.html", user=user)



@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        sha256().update(password.encode())
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        telephone = request.form.get("telephone")
        poids = request.form.get("poids")
        cotisation = request.form.get("cotisation") == "1"

        # Debug : Afficher les valeurs récupérées
        print(f"username={username}, password={password}, nom={nom}, prenom={prenom}, telephone={telephone}, poids={poids}, cotisation={cotisation}")

        if not username or not password or not nom or not prenom or not telephone or not poids:
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template("register.html")

        try:
            cursor = mysql.connection.cursor()

            # Créer un adhérent
            query_adherent = """
                INSERT INTO Adherent (nom, prenom, telephone, poids, cotisation)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_adherent, (nom, prenom, telephone, poids, cotisation))
            print("Adherent créé avec succès.")

            # Créer un utilisateur associé
            query_user = """
                INSERT INTO User (username, password, nom, prenom, role)
                VALUES (%s, %s, %s, %s, 'adherent')
            """
            cursor.execute(query_user, (username, password, nom, prenom))
            print("Utilisateur créé avec succès.")

            # Commit des modifications
            mysql.connection.commit()
            cursor.close()

            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            mysql.connection.rollback()
            print(f"Erreur lors de l'inscription : {e}")  # Debug
            flash(f"Erreur lors de l'inscription : {str(e)}", "danger")

    return render_template("register.html")




@app.route("/poney")
def poney():
    return render_template("poney.html")

@app.route("/reservation/<id>")
def reservation(id):
    cours = get_cours_programme_by_id(id)
    listeponey = get_poney_dispo(id)
    return render_template("reservation.html", cours=cours, listeponey=listeponey, id = id)


import datetime
def semaine(current_week):
    semaine_courante = current_week
    aujourd_hui = datetime.date.today()
    debut_annee = datetime.date(aujourd_hui.year, 1, 1)
    
    lundi = (7 - debut_annee.weekday()) % 7
    premier_lundi = debut_annee + datetime.timedelta(days=lundi)
    
    lundi_de_la_semaine = premier_lundi + datetime.timedelta(weeks=semaine_courante-2 )
    
    dates_de_la_semaine = {}
    for i, nom_du_jour in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
        date_du_jour = lundi_de_la_semaine + datetime.timedelta(days=i)
        dates_de_la_semaine[nom_du_jour] = date_du_jour
    return dates_de_la_semaine

@app.route("/planning", defaults={"current_week": None})
@app.route("/planning/<int:current_week>")
def planning(current_week):
    if current_week is None:
        current_week = datetime.now().isocalendar()[1]

    cursor = mysql.connection.cursor()

    # Requête SQL pour récupérer les cours de la semaine
    query = """
        SELECT 
            idCours, Duree, DateJour, Semaine, Heure, Prix, Niveau, NbPersonne, DAYNAME(DateJour) AS Jour
        FROM 
            CoursProgramme 
        WHERE 
            Semaine = %s
    """
    
    cursor.execute(query, (current_week,))
    cours_raw = cursor.fetchall()
    cursor.close()
    dates = semaine(current_week)

    cours = [
        {
            "id": row[0],
            "duree": row[1],
            "date": row[2],
            "semaine": row[3],
            "heure": row[4].seconds // 3600, 
            "prix": row[5],
            "niveau": row[6],
            "nb_personne": row[7],
            "jour": row[8],
        }
        for row in cours_raw
    ]

    return render_template("planning.html", cours=cours, current_week=current_week, datetime=datetime, dates = dates)




@app.route("/adherer")
def adherer():
    return render_template("adherer.html")

@app.route("/detail_cours/<id>")
def detail_cours(id):
    cours = get_cours_programme_by_id(id)
    return render_template("detail_cours.html", cours=cours)

@app.route("/admin/")
@login_required
def admin():
    if current_user.username == 'admin':
        moniteurs = get_moniteurs()
        utilisateurs = get_utilisateurs()
        return render_template("admin.html", moniteurs=moniteurs, utilisateurs=utilisateurs)
    else:
        flash("Accès réservé à l'administrateur.", "danger")
        return redirect(url_for("home"))
    

@app.route("/moniteur/")
@login_required
def moniteur():
    if current_user.role == 'moniteur':
        return render_template("moniteur.html")
    else:
        flash("Accès réservé au moniteurs.", "danger")
        return redirect(url_for("home"))
    
    

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



@app.route("/admin/create-moniteur", methods=["GET", "POST"])
@login_required
def create_moniteur():
    # Vérification des droits administrateur
    if current_user.username != "admin":
        flash("Accès réservé à l'administrateur.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        # Récupérer les données du formulaire
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        username = request.form.get("username")
        password = request.form.get("password")

        # Validation des données
        if not nom or not prenom or not username or not password:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("create_moniteur"))

        try:
            cursor = mysql.connection.cursor()

            # Vérifier si le username existe déjà
            query_user_check = "SELECT username FROM User WHERE username = %s"
            cursor.execute(query_user_check, (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Ce nom d'utilisateur est déjà utilisé.", "danger")
                return redirect(url_for("admin"))

            # Créer un moniteur
            query_moniteur = """
                INSERT INTO Moniteur (nom, prenom)
                VALUES (%s, %s)
            """
            cursor.execute(query_moniteur, (nom, prenom))
            moniteur_id = cursor.lastrowid  # ID du moniteur inséré

            # Créer un utilisateur avec le rôle moniteur
            query_user = """
                INSERT INTO User (username, password, nom, prenom, role)
                VALUES (%s, %s, %s, %s, 'moniteur')
            """
            cursor.execute(query_user, (username, password, nom, prenom))

            # Confirmer les changements
            mysql.connection.commit()
            cursor.close()

            flash("Moniteur créé avec succès.", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de la création : {str(e)}", "danger")
            return redirect(url_for("admin"))

    return render_template("create_moniteur.html")

