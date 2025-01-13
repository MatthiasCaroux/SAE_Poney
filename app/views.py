# from app import app
from hashlib import sha256
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date, timedelta
from flask import render_template, request
from app.models import *
from app import mysql, login_manager
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from flask import flash, redirect, url_for

UPLOAD_FOLDER = 'static/images'  # Chemin où les fichiers seront stockés
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Extensions autorisées


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        if password != "admin":
            m = sha256()
            m.update(password.encode())
            hashed_password = m.hexdigest()
        else:
            hashed_password = password

        cursor = mysql.connection.cursor()
        query = "SELECT username, password, role FROM User WHERE username = %s "
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[1] == hashed_password:
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

            
            m = sha256()
            m.update(password.encode())
            hashed_password = m.hexdigest()

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
            cursor.execute(query_user, (username, hashed_password, nom, prenom))
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

    cursor = mysql.connection.cursor()
    query = """
        SELECT *
        FROM Poney
        ORDER BY Poney.nomPoney
    """
    cursor.execute(query)
    poneys = cursor.fetchall()
    cursor.close()

    return render_template("poney.html", poneys=poneys)

@app.route("/reservation/<id>")
def reservation(id):
    cours = get_cours_programme_by_id(id)
    prenom,nom = get_prenom_nom_by_current_user(current_user.username)
    user = get_user(prenom,nom)
    poids = get_adherent(prenom,nom).poids
    listeponey = get_poney_dispo(id,poids)
    return render_template("reservation.html", cours=cours, listeponey=listeponey, id = id)


def ajuster_semaine(annee, semaine):
    """
    Ajuste la semaine pour qu'elle boucle correctement entre la première et la dernière semaine de l'année.
    Si la semaine est inférieure à 1, elle passe à la dernière semaine de l'année précédente.
    Si la semaine est supérieure au nombre de semaines de l'année, elle passe à la première semaine de l'année suivante.
    """
    nombre_semaines = date(annee, 12, 28).isocalendar()[1]  # Utilisation correcte de `date`

    if semaine < 1:  
        annee -= 1  
        semaine = date(annee, 12, 28).isocalendar()[1]  # Ajuster pour l'année précédente
    elif semaine > nombre_semaines:  
        annee += 1  
        semaine = 1  # Ajuster pour l'année suivante

    return annee, semaine



def semaine(current_week):
    semaine_courante = current_week
    aujourd_hui = date.today()
    debut_annee = date(aujourd_hui.year, 1, 1)
    
    lundi = (7 - debut_annee.weekday()) % 7
    premier_lundi = debut_annee + timedelta(days=lundi)
    
    lundi_de_la_semaine = premier_lundi + timedelta(weeks=semaine_courante-2 )
    
    dates_de_la_semaine = {}
    for i, nom_du_jour in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
        date_du_jour = lundi_de_la_semaine + timedelta(days=i)
        dates_de_la_semaine[nom_du_jour] = date_du_jour
    return dates_de_la_semaine


def calculer_dates_semaine(annee, semaine):
    """
    Retourne les dates des jours d'une semaine donnée (lundi à dimanche).
    """
    lundi = date.fromisocalendar(annee, semaine, 1)  # Utilisation correcte de `date`
    return {
        "Monday": lundi,
        "Tuesday": lundi + timedelta(days=1),
        "Wednesday": lundi + timedelta(days=2),
        "Thursday": lundi + timedelta(days=3),
        "Friday": lundi + timedelta(days=4),
        "Saturday": lundi + timedelta(days=5),
        "Sunday": lundi + timedelta(days=6),
    }

 
@app.route("/planning", methods=["GET"])
def planning():
    current_year = request.args.get('current_year', default=None, type=int)
    current_week = request.args.get('current_week', default=None, type=int)

    today = date.today()  # Utilisation correcte de `date.today()`

    if current_year is None or current_week is None:
        current_year = today.year
        current_week = today.isocalendar()[1]

    current_year, current_week = ajuster_semaine(current_year, current_week)
    dates = calculer_dates_semaine(current_year, current_week)

    cursor = mysql.connection.cursor()
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

    return render_template("planning.html", cours=cours, current_week=current_week, dates=dates, current_year=current_year)




@app.route("/adherer")
def adherer():
    return render_template("adherer.html")

@app.route("/detail_cours/<id>")
@login_required
def detail_cours(id):
    # Récupérer les détails du cours
    cours = get_cours_by_id(id)

    # Initialiser la liste des participants vide
    participants = []

    # Si l'utilisateur est moniteur ou admin, récupérer les participants
    if current_user.role in ["moniteur", "admin"]:
        participants = get_participants_by_cours_id(id)

    return render_template("detail_cours.html", cours=cours, participants=participants)


@app.route("/admin/")
@login_required
def admin():
    if current_user.username == 'admin':
        # Récupérer les informations des moniteurs
        moniteurs = get_moniteurs()
        utilisateurs = get_utilisateurs()
        poneys = get_poneys()

        # Construire le dictionnaire des poneys
        dico_poney = {}
        for poney in poneys:
            dico_poney[poney[0]] = {"nomPoney": poney[1], "charge_max": poney[2]}

        # Préparer les données pour le graphique
        labels = [f"{moniteur[1]} {moniteur[2]}" for moniteur in moniteurs]  # Prénom + Nom
        data = [float(moniteur[4]) for moniteur in moniteurs]  # Total d'heures prévues
        colors = [
            "rgba(255, 99, 132, 0.5)",
            "rgba(54, 162, 235, 0.5)",
            "rgba(255, 206, 86, 0.5)",
            "rgba(75, 192, 192, 0.5)",
            "rgba(153, 102, 255, 0.5)"
        ] * (len(moniteurs) // 5 + 1)  # Génération de couleurs dynamiques

        return render_template(
            "admin.html",
            moniteurs=moniteurs,
            utilisateurs=utilisateurs,
            dico_poney=dico_poney,
            labels=labels,
            data=data,
            colors=colors
        )
    else:
        flash("Accès réservé à l'administrateur.", "danger")
        return redirect(url_for("home"))

    

@app.route("/moniteur/")
@login_required
def moniteur():
    if current_user.role == 'moniteur':
        # Récupérer l'ID du moniteur
        id_moniteur = get_moniteur_id(current_user.username)
        print(f"ID Moniteur récupéré : {id_moniteur}")

        if not id_moniteur:
            flash("Impossible de récupérer votre identifiant de moniteur.", "danger")
            return redirect(url_for("home"))

        # Récupérer les cours que le moniteur anime
        cursor = mysql.connection.cursor()
        query_cours_animes = """
            SELECT 
                CoursProgramme.DateJour, 
                CoursProgramme.Heure, 
                CoursProgramme.Niveau, 
                CoursProgramme.NbPersonne, 
                CoursRealise.idCoursRealise
            FROM Anime
            JOIN CoursRealise ON Anime.idCours = CoursRealise.idCoursRealise
            JOIN CoursProgramme ON CoursRealise.idCours = CoursProgramme.idCours
            WHERE Anime.idMoniteur = %s;
        """
        cursor.execute(query_cours_animes, (id_moniteur,))
        cours_animes_raw = cursor.fetchall()
        cursor.close()

        cours_animes = [
            {
                "DateJour": row[0],
                "Heure": row[1],
                "Niveau": row[2],
                "NbPersonne": row[3],
                "idCours": row[4]
            }
            for row in cours_animes_raw
        ]

        # Récupérer les cours sans moniteur
        cursor = mysql.connection.cursor()
        query_sans_moniteur = """
            SELECT 
                CoursProgramme.idCours, 
                CoursProgramme.DateJour, 
                CoursProgramme.Heure, 
                CoursProgramme.Niveau, 
                CoursProgramme.NbPersonne,
                CoursRealise.idCoursRealise
            FROM CoursRealise
            JOIN CoursProgramme ON CoursRealise.idCours = CoursProgramme.idCours
            WHERE CoursRealise.idCoursRealise NOT IN (
                SELECT Anime.idCours FROM Anime
            )
        """
        cursor.execute(query_sans_moniteur)
        cours_sans_moniteur_raw = cursor.fetchall()
        cursor.close()

        cours_sans_moniteur = [
            {
                "idCoursRealise": row[5],
                "DateJour": row[1],
                "Heure": row[2],
                "Niveau": row[3],
                "NbPersonne": row[4],
            }
            for row in cours_sans_moniteur_raw
        ]


        return render_template(
            "moniteur.html", 
            cours_animes=cours_animes, 
            cours_sans_moniteur=cours_sans_moniteur
        )
    else:
        flash("Accès réservé aux moniteurs.", "danger")
        return redirect(url_for("home"))



@app.route("/insert_reserver/<id>", methods=["GET", "POST"])
@login_required
def insert_reserver(id):
    if request.method == "POST":

        poney_id = request.form.get("poney")  
        if not poney_id:
            return redirect(url_for('reservation', id=id))  

        # Récupérer l'ID de l'adhérent
        prenom,nom = get_prenom_nom_by_current_user(current_user.username)
        user = get_user(prenom,nom)
        adherent = get_adherent(prenom,nom)
        if adherent:
            adherent_id = adherent.idAdherent
            poids = adherent.poids
        else:
            return redirect(url_for('reservation', id=id))

        # Insérer la réservation
        idcours_realise = get_cours_realise_by_id_programme(id)
        try:
            print(id, adherent_id, poney_id)
            cursor = mysql.connection.cursor()
            query_insert = """
                INSERT INTO Reserver (idCoursRealise, idAdherent, idPoney)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_insert, (idcours_realise, adherent_id, poney_id))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('planning'))  
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

        m = sha256()
        m.update(password.encode())
        hashed_password = m.hexdigest()


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
            cursor.execute(query_user, (username, hashed_password, nom, prenom))

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


@app.route("/all_reservation")
def all_reservation():
    prenom,nom = get_prenom_nom_by_current_user(current_user.username)
    adherent = get_adherent(prenom,nom)
    reservations =get_reservation_by_adherent(adherent.idAdherent)
    listecours = dict()
    listeponey = dict()
    for reservation in reservations:
        listecours[reservation.idReserver] = get_cours_programme_by_id(reservation.idCoursRealise)
        listeponey[reservation.idReserver] = get_poney_by_id(reservation.idPoney)
        print(listecours[reservation.idReserver].date)
        print(listeponey[reservation.idReserver].nomPoney)
    print(reservations)
    print
    return render_template("all_reservation.html",reservations=reservations,listecours=listecours,listeponey=listeponey)



@app.route("/moniteur/create-cours", methods=["GET", "POST"])
@login_required
def create_cours():

    if current_user.role != 'moniteur':
        flash("Accès réservé aux moniteurs.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        # Récupération des données du formulaire
        duree = request.form.get("duree")
        date = request.form.get("date")
        heure = request.form.get("heure")
        prix = request.form.get("prix")
        niveau = request.form.get("niveau")
        nb_personne = request.form.get("nb_personne")

        print(f"Données reçues : {duree}, {date}, {heure}, {prix}, {niveau}, {nb_personne}")

        # Validation des données
        if not duree or not date or not heure or not prix or not niveau or not nb_personne:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("create_cours"))

        try:
            # Conversion des champs de date et heure
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            semaine = date_obj.isocalendar()[1]
            mois = date_obj.month

            # Récupération de l'ID du moniteur
            cursor = mysql.connection.cursor()
            query_moniteur = """
                SELECT Moniteur.idMoniteur
                FROM User 
                NATURAL JOIN Moniteur
                WHERE User.username = %s
            """
            cursor.execute(query_moniteur, (current_user.username,))
            moniteur_row = cursor.fetchone()
            if not moniteur_row:
                flash("Impossible de récupérer l'identifiant du moniteur.", "danger")
                return redirect(url_for("create_cours"))
            id_moniteur = moniteur_row[0]
            cursor.close()

            print(f"ID Moniteur : {id_moniteur}")

            # Création dans CoursProgramme
            cursor = mysql.connection.cursor()
            query_cours_programme = """
                INSERT INTO CoursProgramme (Duree, DateJour, Semaine, Heure, Prix, Niveau, NbPersonne)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_cours_programme, (duree, date, semaine, heure, prix, niveau, nb_personne))
            cours_programme_id = cursor.lastrowid
            mysql.connection.commit()
            cursor.close()
            print(f"ID CoursProgramme créé : {cours_programme_id}")

            # Création dans CoursRealise
            cursor = mysql.connection.cursor()
            query_cours_realise = """
                INSERT INTO CoursRealise (idCours, DateJour, Semaine, Mois)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_cours_realise, (cours_programme_id, date, semaine, mois))
            cours_realise_id = cursor.lastrowid
            mysql.connection.commit()
            cursor.close()
            print(f"ID CoursRealise créé : {cours_realise_id}")

            # Association avec le moniteur dans Anime
            cursor = mysql.connection.cursor()
            query_anime = """
                INSERT INTO Anime (idMoniteur, idCours)
                VALUES (%s, %s)
            """
            cursor.execute(query_anime, (id_moniteur, cours_realise_id))
            mysql.connection.commit()
            cursor.close()
            print("Cours lié au moniteur avec succès.")

            flash("Cours créé avec succès.", "success")
            return redirect(url_for("moniteur"))
        except Exception as e:
            mysql.connection.rollback()
            print(f"Erreur lors de la création : {e}")
            flash(f"Erreur lors de la création : {e}", "danger")
            return redirect(url_for("moniteur"))

    return render_template("create_cours.html")



@app.route("/admin/create-cours", methods=["GET", "POST"])
@login_required
def admin_create_cours():
    if current_user.role != 'admin':
        flash("Accès réservé à l'administrateur.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        # Récupération des données du formulaire
        duree = request.form.get("duree")
        date = request.form.get("date")
        heure = request.form.get("heure")
        prix = request.form.get("prix")
        niveau = request.form.get("niveau")
        nb_personne = request.form.get("nb_personne")

        print(f"Données reçues : {duree}, {date}, {heure}, {prix}, {niveau}, {nb_personne}")

        # Validation des données
        if not duree or not date or not heure or not prix or not niveau or not nb_personne:
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("admin_create_cours"))

        try:
            # Conversion des champs de date et heure
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            semaine = date_obj.isocalendar()[1]
            mois = date_obj.month

            # Création dans CoursProgramme
            cursor = mysql.connection.cursor()
            query_cours_programme = """
                INSERT INTO CoursProgramme (Duree, DateJour, Semaine, Heure, Prix, Niveau, NbPersonne)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_cours_programme, (duree, date, semaine, heure, prix, niveau, nb_personne))
            cours_programme_id = cursor.lastrowid
            mysql.connection.commit()
            cursor.close()
            print(f"ID CoursProgramme créé : {cours_programme_id}")

            # Création dans CoursRealise
            cursor = mysql.connection.cursor()
            query_cours_realise = """
                INSERT INTO CoursRealise (idCours, DateJour, Semaine, Mois)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_cours_realise, (cours_programme_id, date, semaine, mois))
            mysql.connection.commit()
            cursor.close()
            print("Cours créé avec succès.")

            flash("Cours créé avec succès.", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            mysql.connection.rollback()
            print(f"Erreur lors de la création : {e}")
            flash(f"Erreur lors de la création : {e}", "danger")
            return redirect(url_for("admin"))

    return render_template("admin_create_cours.html")


@app.route("/moniteur/animer/<int:id_cours_realise>", methods=["POST"])
@login_required
def animer_cours(id_cours_realise):
    if current_user.role != "moniteur":
        flash("Accès réservé aux moniteurs.", "danger")
        return redirect(url_for("moniteur"))

    try:
        # Récupérer l'ID du moniteur
        cursor = mysql.connection.cursor()
        query_moniteur = """
            SELECT Moniteur.idMoniteur
            FROM User 
            NATURAL JOIN Moniteur
            WHERE User.username = %s
        """
        cursor.execute(query_moniteur, (current_user.username,))
        id_moniteur = cursor.fetchone()

        if not id_moniteur:
            flash("Impossible de récupérer votre identifiant de moniteur.", "danger")
            return redirect(url_for("moniteur"))

        id_moniteur = id_moniteur[0]

        # Vérifier que le cours existe
        query_check_cours = """
            SELECT idCoursRealise FROM CoursRealise WHERE idCoursRealise = %s
        """
        cursor.execute(query_check_cours, (id_cours_realise,))
        cours_existe = cursor.fetchone()

        if not cours_existe:
            flash("Le cours sélectionné n'existe pas.", "danger")
            return redirect(url_for("moniteur"))

        # Vérifier si le cours est déjà assigné
        query_check_anime = """
            SELECT COUNT(*) FROM Anime WHERE idCours = %s
        """
        cursor.execute(query_check_anime, (id_cours_realise,))
        deja_assigne = cursor.fetchone()[0]

        if deja_assigne:
            flash("Ce cours est déjà animé par un moniteur.", "warning")
            return redirect(url_for("moniteur"))

        # Insérer dans Anime
        query_insert_anime = """
            INSERT INTO Anime (idMoniteur, idCours)
            VALUES (%s, %s)
        """
        cursor.execute(query_insert_anime, (id_moniteur, id_cours_realise))
        mysql.connection.commit()
        cursor.close()

        flash("Le cours a été associé avec succès.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Erreur inattendue : {e}", "danger")
    finally:
        return redirect(url_for("moniteur"))




@app.route("/admin/ajouter_poney", methods=["GET", "POST"])
@login_required
def ajouter_poney():
    if current_user.username != "admin":
        flash("Accès réservé à l'administrateur.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        nom = request.form.get("nom")
        charge_max = request.form.get("charge_max")
        description = request.form.get("description")

       
        if not nom or not charge_max or not description :
            flash("Tous les champs sont obligatoires.", "danger")
            return redirect(url_for("ajouter_poney"))

        try:
            # Valider que charge_max est un nombre
            charge_max = float(charge_max)
        except ValueError:
            flash("Le poids du poney doit être un nombre valide.", "danger")
            return redirect(url_for("ajouter_poney"))

        try:
            cursor = mysql.connection.cursor()
            query = """
                INSERT INTO Poney (nomPoney, charge_max, description, image)
                VALUES (%s, %s, %s,/static/images/pepito.jpg) 
            """
            cursor.execute(query, (nom, charge_max,description))
            mysql.connection.commit()
            cursor.close()

            flash("Poney ajouté avec succès.", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", "danger")
            return redirect(url_for("ajouter_poney"))

    return render_template("ajouter_poney.html")
