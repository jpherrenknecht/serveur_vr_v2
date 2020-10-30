import os
import time
import math
import numpy as np
import xarray as xr
import pandas as pd
import json
from datetime import timedelta
import sys 
from uploadgrib import *
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



def f_isochrone(l, temps_initial_iso):
    ''' Calcule le nouvel isochrone a partir d'un tableau de points pt2cplx tableau numpy de cplx'''
    ''' deltatemps, tig , U, V sont supposees etre des variables globales'''
    ''' Retourne les nouveaux points el le nouveau temps et implemente le tableau general des isochrones'''
    global isochrone,TWS,TWD
# il faudrait ajouter aux points l'amure recupere sur l'isochrone
    points=(isochrone[-l:,0:2])
    points2=(isochrone2[-l:,[0,1,5]])  # ici on selectionne -l lignes en partant du bas et les colonnes 0 1 6
    
    numero_iso           = int(isochrone[-1][2] + 1)
    delta_temps          = intervalles[numero_iso]  # Ecart de temps entre anciens points et nouveaux en s
    nouveau_temps        = temps_initial_iso + delta_temps
    t_iso_formate        = time.strftime(" %d %b %Y %H: %M: %S ", time.localtime(temps_initial_iso + delta_temps))
    numero_dernier_point = int(isochrone[-1][4])                   # dernier point isochrone precedent
    numero_premier_point = int(isochrone[-1][4]) - points.shape[0]   # premier point isochrone precedent
    but                  = False 
    # on recupere toutes les previsions meteo d'un coup pour l'ensemble des points de depart
    # TWS, TWD = prevision_tableau3(tig, GR, temps_initial_iso, points)

## Ici il faut rajouter une colonne pour la TWA pour arriver au nouveau point    
    points_calcul=np.array([[0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules
# variante la derniere colonne sert pour la TWA
    points_calcul2=np.array([[0,0,0,0,0,0,0,0]]) # initialisation pour Numpy du brouillard des points calcules  
# pour chacun des points de l'isochrone 







def main():
    t0=time.time() 
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

# Definition des variables pour le routage
    tig, GR        = chargement_grib()
    A= x1+y1*1j                         # Arrivee sous forme complexe
    pt1_np=np.array([[x0,y0]])          # isochrone de depart (1 point)
    # variante avec amure
    pt2_np=np.array([[xn,yn,True]]) 

    print ('(146) pt1_np',pt1_np)
    print ('(147) pt2_np',pt2_np)
    
    amur_init=True                      # amure initiale par defaut tribord

    l=pt1_np.shape[0]                   # longueur de l'isochrone de depart (1)
    temps=t0                            # Definition du temps à l'isochrone de depart par defaut time.time()
    angle_objectif = 90                 # amplitude des angle balayes vers l'objectif 
    temps_mini = 0                      # temps entre le dernier isochrone et l'objectif 
# definition des temps des isochrones
    dt1           = np.ones(72) * 600  # intervalles de temps toutes les 10mn pendant une heure puis toutes les heures
    dt2           = np.ones(370) * 3600
    intervalles   = np.concatenate(([t0 - tig], dt1, dt2))
    temps_cumules = np.cumsum(intervalles)
    but = False
    isochrone = np.array([[x0, y0, 0, 0, 0]])# on initialise le tableau isochrone et TWS TWD
    isochrone2 = np.array([[x0, y0, 0, 0, 0, 1]])# on initialise le tableau isochrone et TWS TWD la derniere colonne ajoutee est l'amure
    TWS, TWD = prevision_tableau3(tig, GR, t0, pt1_np)  
    print ('(137  premier TWS',TWS) 
# on imprime les donnees de depart    
    print()
    print('Depart :      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y0, x0))
    print('Arrivee:      Latitude {:6.4f}     \tLongitude {:6.4f}'.format(y1, x1))
    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    print('Heure UTC du dernier Grib             ',tig_formate_utc)
    print('Heure Locale de depart de la prevision',tic_formate_local)
    print ('Ecart en heures ( = ecart - ecartUTC ) ', (tic-tig)/3600)
    print() 























if __name__ == '__main__':
  
    tic=time.time()
    main()


    











# # Pour test
# tws=12
# twd=150
# HDG = np.array([100, 101, 102,154,185])  # caps
# res4 = polaire2_vect(polaires, tws, twd, HDG)
# print('polaires calculees  ', res4)
# print()
