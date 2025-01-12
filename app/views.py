# from app import app
from datetime import *
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
    prenom,nom = get_nom_prenom_by_current_user(current_user.username)
    user = get_user(prenom,nom)
    poids = get_adherent(prenom,nom).poids
    listeponey = get_poney_dispo(id,poids)
    return render_template("reservation.html", cours=cours, listeponey=listeponey, id = id)



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


        # Récupérer les cours que le moniteur anime
        cursor = mysql.connection.cursor()
        query_cours_animes = """
            SELECT DateJour, Heure, Niveau, NbPersonne, idCours
            FROM Moniteur 
            NATURAL JOIN Anime 
            NATURAL JOIN CoursRealise 
            NATURAL JOIN CoursProgramme 
            WHERE idMoniteur = %s;
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
            SELECT idCoursRealise, DateJour, Heure, Niveau, NbPersonne
            FROM CoursProgramme
            natural join CoursRealise 
            WHERE idCoursRealise NOT IN (
                SELECT idCours FROM Anime
            )
        """
        cursor.execute(query_sans_moniteur)
        cours_sans_moniteur_raw = cursor.fetchall()
        cursor.close()

        # Transformation des données
        cours_sans_moniteur = [
            {
                "idCoursRealise": row[0],
                "DateJour": row[1],
                "Heure": row[2],
                "Niveau": row[3],
                "NbPersonne": row[4],
            }
            for row in cours_sans_moniteur_raw
        ]


        # Renvoyer les données au template
        return render_template("moniteur.html", cours_animes=cours_animes, cours_sans_moniteur=cours_sans_moniteur, poney=poney)

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
        prenom,nom = get_nom_prenom_by_current_user(current_user.username)
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


@app.route("/all_reservation")
def all_reservation():
    nom,prenom = get_nom_prenom_by_current_user(current_user.username)
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


@app.route("/moniteur/animer/<int:id_cours>", methods=["POST"])
@login_required
def animer_cours(id_cours):
    if current_user.role != "moniteur":
        flash("Accès réservé aux moniteurs.", "danger")
        return redirect(url_for("moniteur"))

    try:
        # Récupération de l'ID du moniteur
        cursor = mysql.connection.cursor()
        query = """
            SELECT Moniteur.idMoniteur
            FROM User 
            NATURAL JOIN Moniteur
            WHERE User.username = %s
        """
        cursor.execute(query, (current_user.username,))
        id_moniteur = cursor.fetchone()[0]
        cursor.close()

        # Insertion dans Anime
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO Anime (idMoniteur, idCours)
            VALUES (%s, %s)
        """
        cursor.execute(query, (id_moniteur, id_cours))
        mysql.connection.commit()
        cursor.close()

        flash("Le cours a été associé avec succès.", "success")
    except mysql.connector.Error as err:
        # Gestion spécifique de l'erreur SQL 1644
        if err.errno == 1644:
            flash(f"Erreur lors de l'ajout : {err.msg}", "danger")
        else:
            flash("Une erreur inattendue s'est produite.", "danger")
    except Exception as e:
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

        if not nom or not charge_max:
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
                INSERT INTO Poney (nomPoney, charge_max)
                VALUES (%s, %s)
            """
            cursor.execute(query, (nom, charge_max))
            mysql.connection.commit()
            cursor.close()

            flash("Poney ajouté avec succès.", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Erreur lors de l'ajout : {str(e)}", "danger")
            return redirect(url_for("ajouter_poney"))

    return render_template("ajouter_poney.html")
