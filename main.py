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


app = Flask(__name__)
app.secret_key="Hello"
app.permanent_session_lifetime = timedelta(days=1)     
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy(app)

tic=time.time()
#tig, GR ,filename       = chargement_grib()
nb_points_ini=20




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


# @app.route('/courses')
# def config():
#     with open('courses.json','r') as f:
#         return Response(headers={'Content-Type':'application/json'},response=f.read())

@app.route('/testpython')
def testpython():
    v1=10250
    v2='Bonjour la france'
     
    return render_template('testpython.html',variablenumerique=v1,variabletexte=v2)

 




if __name__ == '__main__':
    app.run(debug=True)






@app.route('/windleaf',methods =["GET", "POST"])
def windleaf():

    tsimul=time.time()
    global x0,y0,x1,y1,nb_points_ini,nb_points_sec ,tig,GR
    tig, GR,filename        = chargement_grib()
    #**********************************************************************************
    nb_points_ini=200
    nb_points_sec=50 
    #**********************************************************************************
    
    # valeurs par defaut si pas de retour de dashboard
    course="440.1"
    depart="depart"
    arrivee="bouee21"
    nomcourse="Vendee Globe"
    bateau="imoca60vg"

    with open('static/js/courses.json', 'r') as fichier:                      # change dans fichier courants
        data1 = json.load(fichier)
        latar  = (data1[course][arrivee]["lat"])
        lngar  = (data1[course][arrivee]["lng"])

    try:
        (request.args['latdep'])
        latdep = -float(request.args['latdep'])
        lngdep = float(request.args['lngdep'])
        course = request.args['race']
        nomcourse=data1[course]['nom']
        bateau=data1[course]['bateau']
        # print('On est dans try : Valeurs récupérées par get')
        # print ('latdep lngdep ',latdep,lngdep )  

    except :   
        
        # print ('course',course)
        # bateau=  (data1[course]["bateau"])
        lat1 = (data1[course][depart]["lat"])
        lng1 = (data1[course][depart]["lng"])
        lngdep,latdep=chaine_to_dec(lat1, lng1)
        nomcourse=data1[course]["nom"]
        bateau=data1[course]['bateau']
        # print('on est dans except')
        # print ('latdep lngdep ',latdep,lngdep )  

    try :
        (request.args['latar'])
        lngar = -float(request.args['latar'])    #interversion a corriger et corriger dans fonction routeur
        latar = float(request.args['lngar'])
      
    except:
        lat2  = (data1[course][arrivee]["lat"])
        lng2  = (data1[course][arrivee]["lng"])    
        latar,lngar=chaine_to_dec(lat2, lng2)    # la aussi il y a inversion
      

  
    # chargement du grib partiel pour utilisation ulterieure en js
   # global tig, GR,filename
    latini=(math.floor(-latdep)+10)    # latitude la plus au nord en premier et latitude nord negative pour charger le grib pour javascript
    latfin=(latini -20)
    lngini=(math.floor(lngdep)-20)%360
    lngfin=(lngini+40)%360
    u10,v10=vents_encode2(latini,latfin,lngini,lngfin)   
   
    
    
    # calcul de la route et de la multipolyline des isochrones
       
    multipolyline,route,comment,x0,y0,x1,y1,l1,l2,polairesjs2=fonction_routeur(course,latdep,lngdep,latar,lngar,tsimul)
    latar=y1
    lngar=x1
    red=[]
    black=[]
    for i in range(len(multipolyline)):
        if (i+1)%6==0:
                black.append(multipolyline[i])
        else:
                red.append(multipolyline[i]) 

    # print ('filename',filename)
    
    base=os.path.basename(filename)  
    nomgrib=os.path.splitext(base)[0]    

    print ('Prevision au point de depart')
    vit_vent_n, angle_vent = prevision(tig, GR,tsimul, latdep,lngdep)
    print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    print()     
    # print('nomgrib',nomgrib)
    
    # print ('(630 latdep lngdep dans main.py',latdep,lngdep)
    # print ('(631 latar lngar dans main.py',latar,lngar)

    print ('Chargement du grib pour js entre {:6.3f} {:6.3f} et  {:6.3f} {:6.3f}'.format(latini,latfin,lngini,lngfin))
    print ('Heure de depart de la simulation  {} '.format(time.strftime(" %d %b  %H:%M:%S ", time.localtime(tsimul))))
    print ('course',course)
    print ('Nom de la course: ',nomcourse)
    print ('Bateau',bateau)
    print ('latdep lngdep ',latdep,lngdep )  
    return render_template("windleaf.html", nomgrib=nomgrib, multipolyred=red,multipolyblack=black,course=course,nomcourse=nomcourse,bateau=bateau,route=route,comment=comment,l1=l1,l2=l2,polairesjs=polairesjs2,lngdep=lngdep,latdep=latdep,lngar=lngar,latar=latar, t0=tsimul,tig=tig,latini=latini,lngini=lngini,latfin=latfin,lngfin=lngfin,U10=u10, V10=v10 ,result=request.form)



if __name__ == "__main__" :
    db.create_all()                 #creation de la base de donnees
    app.debug=True
    app.config['JSON_AS_ASCII']=True
    app.run(host='127.0.0.1', port=8100, debug=True)
