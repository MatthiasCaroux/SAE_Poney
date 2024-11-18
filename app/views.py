# from app import app
from flask import render_template
from app.models import *


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/poney")
def poney():

    return render_template("poney.html", poney=get_poney()[:10])