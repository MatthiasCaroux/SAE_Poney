from flask import Flask


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'servinfo-maria'
app.config['MYSQL_USER'] = 'niveau'
app.config['MYSQL_PASSWORD'] = 'niveau'
app.config['MYSQL_DB'] = 'DBniveau' #mettre sa propre BD


if __name__ == '__main__':
    app.run(debug=True)