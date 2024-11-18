from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

import os.path

def mkpath(p):
    return os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            p
        )
    )

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'servinfo-maria'
app.config['MYSQL_USER'] = 'niveau'
app.config['MYSQL_PASSWORD'] = 'niveau'
app.config['MYSQL_DB'] = 'DBniveau' #mettre sa propre BD
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + mkpath('../myapp.db')
)


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

if __name__ == '__main__':
    app.run(debug=True)