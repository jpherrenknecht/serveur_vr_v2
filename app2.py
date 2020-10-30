import os
import time
import math
import numpy as np
import xarray as xr
import pandas as pd
import json
from datetime import timedelta
import sys 
from global_land_mask import globe
from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy
# visualisation folium si necessaire
#import folium
#import webbrowser



tic=time.time()





app = Flask(__name__)
app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     # minutes=10





# Serveur web
@app.route('/')
def index():
  return render_template('index.html')


@app.route('/index2')
def index2():
  return render_template('index2.html')

@app.route('/leafletbase')
def leafletbase():
  return render_template("leafletbase.html")



if __name__ == "__main__" :
    #db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.config['JSON_AS_ASCII']=False
    app.run(host='127.0.0.1', port=8080, debug=True, use_reloader=False)

