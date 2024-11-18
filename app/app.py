from flask import Flask
from flask_login import LoginManager
from flask_mysqldb import MySQL




app = Flask(__name__)

app.config['MYSQL_HOST'] = 'servinfo-maria'
app.config['MYSQL_USER'] = 'niveau'
app.config['MYSQL_PASSWORD'] = 'niveau'
app.config['MYSQL_DB'] = 'DBniveau' #mettre sa propre BD

mysql=MySQL(app)


if __name__ == '__main__':
    app.run(debug=True)