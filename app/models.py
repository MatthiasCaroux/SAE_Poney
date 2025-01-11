from .app import app
from .app import mysql  # Corrected import statement

class Poney:
    def __init__(self, idPoney, nomPoney, charge_max):
        self.idPoney = idPoney
        self.nomPoney = nomPoney
        self.charge_max = charge_max
        self.reservations = []

    def __repr__(self):
        return f"Poney(idPoney={self.idPoney}, nomPoney={self.nomPoney}, charge_max={self.charge_max})"

def get_poney():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM PONEY")
    poney = cursor.fetchall()
    cursor.close()
    res = []
    for p in poney:
        res.append(Poney(p[0], p[1], p[2]))
    return res

class Adherent:
    def __init__(self, idAdherent, poids, nom, cotisation, telephone):
        self.idAdherent = idAdherent
        self.poids = poids
        self.nom = nom
        self.cotisation = cotisation
        self.telephone = telephone

class CoursProgramme:
    def __init__(self, idCours, duree,date,semaine,heure,prix,niveau,nbpersonnes):
        self.idCours = idCours
        self.duree = duree
        self.date = date
        self.semaine = semaine
        self.heure = heure
        self.prix = prix
        self.niveau = niveau
        self.nbpersonnes = nbpersonnes

def get_cours_programme():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM CoursProgramme")
    cours_programme = cursor.fetchall()
    cursor.close()
    res = []
    for c in cours_programme:
        res.append(CoursProgramme(c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]))
    return res

def get_cours_programme_by_id(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM CoursProgramme WHERE idCours = %s", (id,))
    cours_programme = cursor.fetchone()
    cursor.close()
    return CoursProgramme(cours_programme[0], cours_programme[1], cours_programme[2], cours_programme[3], cours_programme[4], cours_programme[5], cours_programme[6], cours_programme[7])


def get_moniteurs():
    cursor = mysql.connection.cursor()
    query = """
        SELECT 
    Moniteur.idMoniteur, 
    Moniteur.nom, 
    Moniteur.prenom, 
    COUNT(Anime.idCours) AS NombreCoursRealises, 
    COALESCE(SUM(CoursProgramme.Duree), 0) AS TotalHeuresPrevues
    FROM Moniteur
    LEFT JOIN Anime ON Moniteur.idMoniteur = Anime.idMoniteur
    LEFT JOIN CoursRealise ON Anime.idCours = CoursRealise.idCoursRealise
    LEFT JOIN CoursProgramme ON CoursRealise.idCours = CoursProgramme.idCours
    GROUP BY Moniteur.idMoniteur, Moniteur.nom, Moniteur.prenom

    UNION

    SELECT 
        Moniteur.idMoniteur, 
        Moniteur.nom, 
        Moniteur.prenom, 
        0 AS NombreCoursRealises, 
        0 AS TotalHeuresPrevues
    FROM Moniteur
    WHERE Moniteur.idMoniteur NOT IN (
        SELECT DISTINCT idMoniteur FROM Anime
    )
    ORDER BY idMoniteur;

    """
    cursor.execute(query)
    moniteurs = cursor.fetchall()
    cursor.close()
    return moniteurs


def get_nombre_heure_travailler(idUser):
    """
    Calcule le nombre total d'heures travaillées pour un utilisateur donné.

    Args:
        idUser (int): L'ID de l'utilisateur (idUser).

    Returns:
        int: Nombre total d'heures travaillées.
    """
    cursor = mysql.connection.cursor()

    # Requête SQL pour récupérer le nombre total d'heures travaillées
    query = """
        SELECT COALESCE(SUM(CoursProgramme.Duree), 0) AS TotalHeures
        FROM User
        JOIN Moniteur ON User.nom = Moniteur.nom AND User.prenom = Moniteur.prenom
        JOIN Anime ON Moniteur.idMoniteur = Anime.idMoniteur
        JOIN CoursRealise ON Anime.idCours = CoursRealise.idCoursRealise
        JOIN CoursProgramme ON CoursRealise.idCours = CoursProgramme.idCours
        WHERE User.idUser = %s
    """
    cursor.execute(query, (idUser,))
    result = cursor.fetchone()
    cursor.close()

    # Retourner le nombre total d'heures travailler
    return result[0] if result else 0




def get_utilisateurs():
    cursor = mysql.connection.cursor()
    # Récupérer uniquement les utilisateurs avec un idConnexion valide
    cursor.execute("SELECT idConnexion, prenom, nom, role FROM User WHERE idConnexion IS NOT NULL")
    utilisateurs = cursor.fetchall()
    cursor.close()
    return utilisateurs


class Poney:
    def __init__(self, idPoney, nomPoney, charge_max):
        self.idPoney = idPoney
        self.nomPoney = nomPoney
        self.charge_max = charge_max
        self.reservations = []

    def __repr__(self):
        return f"Poney(idPoney={self.idPoney}, nomPoney={self.nomPoney}, charge_max={self.charge_max})"

def get_poney():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Poney")
    poney = cursor.fetchall()
    cursor.close()
    res = []
    for p in poney:
        res.append(Poney(p[0], p[1], p[2]))
    return res

def get_poney_dispo(id_cours,poids):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Poney WHERE idPoney NOT IN (SELECT idPoney FROM Reserver WHERE idCoursRealise = %s or charge_max <%s )", (id_cours,poids,))
    poney = cursor.fetchall()
    cursor.close()
    res = []
    for p in poney:
        res.append(Poney(p[0], p[1], p[2]))
    return res

def get_moniteur_id(username_moniteur):
    cursor = mysql.connection.cursor()
    cursor.execute("select idMoniteur from User natural join Moniteur WHERE username = %s", (username_moniteur,))
    moniteur = cursor.fetchone()
    cursor.close()
    return moniteur[0] if moniteur else None


def get_nom_prenom_by_current_user(current_user_username):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT prenom, nom FROM User WHERE username = %s", (current_user_username,))
    result = cursor.fetchone()
    cursor.close()
    return result

class User:
    def __init__(self, idConnexion,password, nom, prenom, role):
        self.idConnexion = idConnexion
        self.password = password
        self.nom = nom
        self.prenom = prenom
        self.role = role

    def __repr__(self):
        return f"User(idConnexion={self.idConnexion}, nom={self.nom}, prenom={self.prenom}, role={self.role})"

def get_user(prenom,nom):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM User WHERE prenom = %s and nom = %s", (prenom,nom,))
    user = cursor.fetchone()
    cursor.close()
    return User(user[0], user[1], user[2], user[3], user[4])

def get_adherent(prenom,nom):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Adherent WHERE prenom = %s and nom = %s", (prenom,nom,))
    adherent = cursor.fetchone()
    cursor.close()
    return Adherent(adherent[0], adherent[1], adherent[2], adherent[3], adherent[4])

