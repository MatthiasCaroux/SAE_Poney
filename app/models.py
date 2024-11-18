from .app import db
from .app import login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

class User(db.Model,UserMixin):
    username = db.Column(db.String(50) , primary_key =True)
    password = db.Column(db.String(64))
    def get_id(self):
        return self.username