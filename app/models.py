from .app import db
from .app import login_manager
from .app import app
from .app import mysql
from flask_login import UserMixin


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

class User(db.Model,UserMixin):
    username = db.Column(db.String(50) , primary_key =True)
    password = db.Column(db.String(64))
    def get_id(self):
        return self.username
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
    cursor.execute("SELECT * FROM Poney")
    poney = cursor.fetchall()
    cursor.close()
    res = []
    print(poney)
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