from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager


app = Flask(__name__)




# app.config['MYSQL_HOST'] = 'servinfo-maria'
# app.config['MYSQL_USER'] = 'niveau'
# app.config['MYSQL_PASSWORD'] = 'niveau'
# app.config['MYSQL_DB'] = 'DBniveau' #mettre sa propre BD
# app.config['SECRET_KEY'] = 'secret'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'matthias1'
# app.config['MYSQL_DB'] = 'sae_poney'
# app.config['SECRET_KEY'] = 'secret'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'niveau'
app.config['MYSQL_DB'] = 'dbniveau'
app.config['SECRET_KEY'] = 'secret'




mysql=MySQL(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'