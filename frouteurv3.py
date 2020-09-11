import os
import time
import math
import numpy as np
import xarray as xr
import pandas as pd
import json
from datetime import timedelta
import sys 
#from uploadgrib import *
from global_land_mask import globe
from flask import Flask, redirect, url_for,render_template, request , session , flash
from flask_sqlalchemy import SQLAlchemy
from modules.fonctions.fonctions1 import *

# visualisation folium si necessaire
import folium
import webbrowser


# voir si necessaire
import matplotlib.pyplot as plt
import pickle
tic=time.time()

#Donnees course
n_course='4633'
depart="dunkerque"
arrivee="ouessant"

# Lecture du fichier json des courses
with open('courses.json', 'r') as fichier:
    data     = json.load(fichier)
    course   = (data[n_course]["nom"])
    bateau   = (data[n_course]["bateau"])
    polaires = (data[n_course]["polaires"])
    latdep   = (data[n_course][depart]["lat"])
    lngdep   = (data[n_course][depart]["lng"])
    latar    = (data[n_course][arrivee]["lat"])
    lngar    = (data[n_course][arrivee]["lng"])

    x0,y0=chaine_to_dec(latdep,lngdep)
    x1,y1=chaine_to_dec(latar,lngar)
    print('\nCourse  : ',course)
    print ('Bateau  : ',bateau)
    print ('Polaires: ',polaires)
    print ('Depart  :   Latitude: {} ({:6.4f}) Longitude: {} ({:6.4f})'.format(latdep,y0 ,lngdep, x0))
    print ('Arrivee :   Latitude: {} ({:6.4f}) Longitude: {} ({:6.4f})'.format(latdep,y0 ,lngdep, x0))
    print()
# importation du fichier de polaires    
val='modules.polaires.'+polaires
exec('from '+val+ ' import *')


# Pour test
tws=12
twd=150
HDG = np.array([100, 101, 102,154,185])  # caps
res4 = polaire2_vect(polaires, tws, twd, HDG)
print('polaires calculees  ', res4)
print()