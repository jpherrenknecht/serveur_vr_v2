# -*- coding: utf-8 -*-
import os
import time
from datetime import timedelta
import math
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import json
from json import dumps
from json import JSONEncoder
import folium
import webbrowser
from uploadgrib3 import *
from fonctions_vr import *
from global_land_mask import globe
import pickle
from flask import Flask, redirect, url_for,render_template, request , session , flash , jsonify
from flask_sqlalchemy import SQLAlchemy

tic=time.time()


from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy
#from frouteur import frouteur


application= app = Flask(__name__)
app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

tic=time.time()
# tests sur lecture ecriture de fichiers json a partir du fichier python
with open('static/js/barriere_glaces.json', 'r') as fichier:                      # change dans fichier courants
        data1 = json.load(fichier)
        
       # print(data1)
        points  = data1['coords']
        # on passe par numpy provisoirement
        nppoints=np.array(points)

        lngs=nppoints[:,0].reshape(-1,1)/1000
        lats=nppoints[:,1].reshape(-1,1)/1000
        poly=np.concatenate((lats,lngs),1)
        polyline=[arr.tolist() for arr in poly]
    
        # on cree un dictionnaire qui sera transforme en json 
        poly_json={'barrieretest': polyline}


# on le sauvegarde sous forme de json
with open("static/js/barriereglaces.json","w") as f :
     json.dump(poly_json,f)

# on peut 

# le recharge eventuellement 
with open('static/js/barriereglaces.json', 'r') as fichier:                      # change dans fichier courants
     data2 = json.load(fichier)



print(data2['barrieretest'][1])



class user(db.Model):                                              # creation du modele de base de donnée
    id     = db.Column(db.Integer, primary_key=True)
    nom    = db.Column(db.String(100))
    prenom = db.Column(db.String(100))


##partie serveur web


@app.route('/')
#html de base pour verifier le fonctionnement
def index():
  return render_template('home.html')

@app.route('/javascript')
#html de base pour verifier le fonctionnement d'importation des fichiers externes
def javascript():
  return render_template('javascript.html')

@app.route('/courses')
def courses():
  return render_template('static/js/courses.json')


@app.route('/testpython')
def testpython():
    v1=10250
    v2='Bonjour la france'
     
    return render_template('testpython.html',variablenumerique=v1,variabletexte=v2)

 






if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    # app.config['JSON_AS_ASCII']=True
    #app.run(host='127.0.0.1', port=8100, debug=True)
