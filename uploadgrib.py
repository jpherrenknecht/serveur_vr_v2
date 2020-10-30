#!/bin/env_vr python3.7.5
# coding: utf-8
import os
import time
import math
import numpy as np
from urllib.request import urlretrieve
import xarray as xr
import h5py
from datetime import datetime
from scipy.interpolate import RegularGridInterpolator
from pathlib import Path
import numba
from numba import jit

# les gribs complets sont disponibles en heure d'ete à
# 13h(gfs06) - 19(gfs12) -  01(gfs18) - 07 h (gfs00)
# les gribs complets sont disponibles en heure d'hiver à
# 12h(gfs06) - 18(gfs12) -  00(gfs18) - 06 h (gfs00)

# renvoie le chemin absolu du repertoire courant ici /home/jphe/PycharmProjects/VR_version2
basedir = os.path.abspath(os.path.dirname(__file__))


ix = np.arange(129)  # temps
iy = np.arange(181)  # latitudes
iz = np.arange(361)  # longitudes


def chainetemps_to_int(chainetemps):
    '''Convertit une chaine de temps en valeur entiere '''
    '''retourne egalement le temps en s ou le temps formate '''
    day = int(chainetemps[0:2])
    month = int(chainetemps[3:5])
    year = int(chainetemps[6:10])
    hour = int(chainetemps[11:13])
    mins = int(chainetemps[14:16])
    secs = int(chainetemps[17:19])
    strhour = chainetemps[11:13]
    date = chainetemps[6:10] + chainetemps[3:5] + chainetemps[0:2]

    #print('strhour : ',strhour)
    #print('date : ',date)

    t = time.localtime()
    utc = time.gmtime()
    decalage_s = (t[3] - utc[3]) * 3600
    t_s_local = time.mktime((year, month, day, hour +1, mins, secs, 0, 0, 0))
    t_s_utc = t_s_local - decalage_s
    #todo pourquoi le +1
    formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(t_s_local))
    # t_s est un temps en secondes locales
    return t_s_local, day, month, year, hour, mins, secs, date, strhour, formate_local, t_s_utc


def chaine_to_dec(latitude, longitude):
    ''' Transforme les chaines latitude et longitude en un tuple (x,y) '''
    degre = int(latitude[0:3])
    minutes = int(latitude[4:6])
    secondes = int(latitude[7:9])
    lat = degre + minutes / 60 + secondes / 3600
    if latitude[10] == 'N':
        lat = -lat
    degre = int(longitude[0:3])
    minutes = int(longitude[4:6])
    secondes = int(longitude[7:9])
    long = degre + minutes / 60 + secondes / 3600
    if longitude[10] == 'W':
        long = -long
    return (long, lat)


def filename():
    ''' retourne le nom du fichier du dernier grib sous lequel le grib chargé sera sauvé ou du dernier grib disponible
       la date du grib et le tig en secondes locales '''
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    heures = [0,6,12,18]
        #on bloque l'heure du grib
    heure_grib = heures[((utc[3] + 19) // 6) % 4]  #
    #si utc inferieur à 5 la date doit etre celle de la veille
    if utc[3]<5:
        utc = time.gmtime(time.time() -18000)
    dategrib =datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
    tig=time.mktime(dategrib.timetuple())+decalage_h*3600

    date= str(dategrib)
    filename="gribs/grib_gfs_" + date + ".hdf5"
    filenamehdf5 = os.path.join(basedir,filename)
    
    #time.time()- tig correspond bien à l'ecart de temps avec le grib
    return filenamehdf5,date,tig


def ouverture_fichier(filename):
    # ouverture du fichier hdf5
    f2 = h5py.File(filename, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig, GR




def chargement_grib():
    '''reconstitue le nom du dernier grib disponible
      le charge sur nmea au besoin 
      et le charge pour la simulation s'il existe deja '''
    t = time.localtime()
    utc = time.gmtime()
    decalage_h = t[3] - utc[3]
    heures = [0,6,12,18]
    heure_grib = heures[((utc[3] + 19) // 6) % 4]  # heure du grib
    #si utc inferieur à 5 la date doit etre celle de la veille l'heure est inchangée
    if utc[3]<5:
        utc = time.gmtime(time.time() -18000)
    dategrib_tpl=datetime(utc[0] , utc[1] , utc[2] , int(heure_grib),0, 0)
    tig=time.mktime(dategrib_tpl.timetuple())+decalage_h*3600    #temps initial du grib en sec locales 
    dategrib= str(dategrib_tpl) 
    date=dategrib[0:10].replace("-","")
    strhour=dategrib[11:13]
    filename="gribs/grib_gfs_" + date +"-"+strhour+".hdf5"
    filenamehdf5 = os.path.join(basedir,filename)

    if os.path.exists(filenamehdf5) == False:        #si ce fichier n'existe pas deja
        leftlon, rightlon, toplat, bottomlat = 0, 360, 90, -90
        iprev = ()
        for a in range(0, 387, 3):  # Construit le tuple des indexs des fichiers maxi 387
            iprev += (str(int(a / 100)) + str(int((a % 100) / 10)) + str(a % 10),)
        GR = np.zeros((len(iprev), 181, 360),
                      dtype=complex)  # initialise le np array de complexes qui recoit les donnees
        for indexprev in range(len(iprev)):  # recuperation des fichiers de 0 a 384 h
            prev = iprev[indexprev]
            url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t" + strhour + "z.pgrb2.1p00.f" + \
                  prev + "&lev_10_m_above_ground=on&all_var=on&leftlon=" \
                  + str(leftlon) + "&rightlon=" + str(rightlon) + "&toplat=" + str(toplat) + "&bottomlat=" + str(
                bottomlat) + "&dir=%2Fgfs." + date + "%2F" + strhour
            nom_fichier = "grib_" + date + "_" + strhour + "_" + prev
            urlretrieve(url, nom_fichier)  # recuperation des fichiers provisoires
            print(' Enregistrement prévision {} + {} heures effectué: '.format(dategrib,prev))  # destine a suivre le chargement des previsions

            # exploitation du fichier et mise en memoire dans GR
            ds = xr.open_dataset(nom_fichier, engine='cfgrib')
            GR[indexprev] = ds.variables['u10'].data + ds.variables['v10'].data * 1j
            os.remove(nom_fichier)  # On efface le fichier pour ne pas encombrer
            os.remove(nom_fichier + '.4cc40.idx')

        # on modifie GR pour lui donner un indice 360 egal à l'indice 0
        GR=np.concatenate((GR,GR[:,:,0:1]), axis=2)

        # sauvegarde dans fichier hdf5 du tableau GR
        #filename = "~/PycharmProjects/VR_version2/gribs/grib_gfs_" + dategrib + ".hdf5"
        f1 = h5py.File(filenamehdf5, "w")
        dset1 = f1.create_dataset("dataset_01", GR.shape, dtype='complex', data=GR)
        dset1.attrs['time_grib'] = tig  # transmet le temps initial du grib en temps local en s pour pouvoir faire les comparaisons
        f1.close()

    # ouverture du fichier hdf5
    f2 = h5py.File(filenamehdf5, 'r')
    list(f2.keys())
    dset1 = f2['dataset_01']
    GR = dset1[:]
    tig = dset1.attrs['time_grib']
    f2.close()
    return tig, GR



def prevision0(tig, GR, tp, latitude, longitude):
    #fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = int((tp - tig) / 3600 / 3)
    ilati = int((latitude + 90))
    ilong = int((longitude) % 360)

    print (GR(0,0,0))

    print ('indices',itemp,ilati,ilong )

    #vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent


@jit
def prevision(tig, GR, tp, latitude, longitude):
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp = (tp - tig) / 3600 / 3
    ilati = (latitude + 90)
    ilong = (longitude) % 360
    #print ('indices',itemp,ilati,ilong )
    vcplx = fn3((itemp, ilati, ilong))
    #print('vcplx',vcplx)
    vit_vent_n = np.abs(vcplx) * 1.94384
    angle_vent = (270 - np.angle(vcplx, deg=True)) % 360
    return vit_vent_n, angle_vent

def prevision_tableau (tig,GR,tp,points):
    '''Le tableau des points est un tableau de points complexes'''
    '''retourne un tableau des previsions angles et vitesses '''
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    itemp=np.ones( points.shape)*(tp - tig) / 3600 / 3
    #print('shape base',points.shape)
    #print ('itemp  base',itemp)
    ilati = np.imag(points) + 90
    #print('ilati base',ilati)
    ilong = np.real(points) %360
    e=np.concatenate((itemp.T,ilati.T,ilong.T ),axis=1)

    #print ('tableau e\n',e)

    # print ('e.shape)',e.shape)
    # print ('e',e)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)

    return vitesse, angle_vent

def prevision_tableau3 (tig,GR,tp,pointsxy):
    '''Le tableau des points est un tableau de points np array x y'''
    '''retourne un tableau des previsions angles et vitesses '''
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)

    itemp=np.ones( pointsxy.shape[0])*(tp - tig) / 3600 / 3
    #print ('itemp ',itemp)
    item =itemp.reshape((-1,1))

    ilati =  pointsxy.T[1] + 90
    #print('ilati',ilati)
    ilat= ilati.reshape((-1,1))

    ilong =  pointsxy.T[0]%360
    #print('ilong',ilong)
    ilon=ilong.reshape((-1,1))
    e=np.concatenate((item,ilat,ilon ),axis=1)

    #print ('e.shape)',e.shape)
    #print ('e',e)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)
    return vitesse, angle_vent
    #return None


def prevision_tableau2 (GR,temp,point):
    ''' calcule les previsions a partir d'une liste des temps par rapport au depart et des points sous forme complexe'''
    temps = temp.reshape((1, -1))
    points=point.reshape((1, -1))
    fn3 = RegularGridInterpolator((ix, iy, iz), GR)
    tab_itemp=temps.reshape((1,-1))/ 3600 / 3
    ilati = np.imag(points) + 90
    ilong = np.real(points) %360
    e = np.concatenate(( tab_itemp.T, ilati.T, ilong.T), axis=1)
    prevs = fn3((e))   #prevs est un tableau de complexes des vecteurs du vent aux differents points
    vitesse = np.abs(prevs) * 1.94384
    #print (vitesse)
    angle_vent = (270 - np.angle(prevs, deg=True)) % 360
    #print (angle_vent)

    return vitesse, angle_vent
    

if __name__ == '__main__':

    #chargement_grib()
    tig, GR = chargement_grib()
    tic = time.time()

    # print()
    # print ('tig en s ',tig)
    # print ('tic en s ',tic)
    # print ('Ecart', (tic-tig)/3600,'h')
    print ('\nPrévision à date et heure données \
            \n---------------------------------')

    tig_formate_utc = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(tig))
    tic_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(tic))
    print('\n Date et Heure UTC du dernier Grib             ',tig_formate_utc) 
    print(' Date et Heure locales                         ',tic_formate_local) 
    


    # Depart
    latitude_d = '051-38-17-N'
    longitude_d = '000-46-19-W'
    d = chaine_to_dec(latitude_d, longitude_d)  # co
    #print ('latitude et longitude',d)
    


# prevision avec date donnee    

   
    print('\n Latitude {:6.2f} et Longitude{:6.2f} '.format( d[1], d[0]))
    dateprev=datetime(2020 , 10 , 10, 18, 0 ,  0)
    #print ('\nDateprev : ',dateprev , ' local')
    # je peux la transformer en secondes mais ce sont des secondes locales
    dateprev_s=time.mktime(dateprev.timetuple())
    #print ('dateprev_s en local ',dateprev_s )
    dateprev_formate_local = time.strftime(" %d %b %Y %H:%M:%S ", time.localtime(dateprev_s))
    print(' Date et heure prévision',dateprev_formate_local)

    #%timeit prevision(tig, GR,dateprev_s, d[1], d[0])

    tic=time.time()
    # prevision proprement dite
    for i in range (1000):
        vit_vent_n, angle_vent = prevision(tig, GR,dateprev_s, d[1], d[0])
    #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
    
    tac=time.time()
    
    print ('temps execution ', (tac-tic), 's')
    print()

    print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
    print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    print()



# # prevision avec temps instantane
#     print ("\nPrévision à l'instant de l'heure locale\
#             \n---------------------------------")
#     print()
#     print('Heure Locale ',tic_formate_local)
#     vit_vent_n, angle_vent = prevision(tig, GR,tic, d[1], d[0])
#   #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
#     print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
#     print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))


# # prevision avec temps instantane
#     print ("\nPrévision corrigee proche VR\
#             \n---------------------------------")
#     print()
#     print('Heure Locale ',tic_formate_local)
#     ticvr=tic+6500
#     vit_vent_n, angle_vent = prevision(tig, GR,ticvr, d[1], d[0])
#   #  print('\nLe {} heure Locale Pour latitude {:6.2f} et longitude{:6.2f} '.format(dateprev_formate_local, d[1], d[0]))
#     print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
#     print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))




    # #version tableau np complexe******************************************************************************

    # points=np.array([[-67-39*1j, -65-40*1j]])
    # points = np.array([[d[0] + d[1] * 1j]])
    # cplx = np.array([[-10 - 2 * 1j, -15 + 3 * 1j, 50 + 10 * 1j]])
    # prevs=prevision_tableau(tig, GR, tic, cplx)
    # print('\nresultat avec tableau',prevs)
    # print()

    # #version tableau np x y******************************************************************************

    # cplx=np.array([[-10 - 2 * 1j, -15 + 3 * 1j, 50 + 10 * 1j]])
    # points=np.concatenate((cplx.real.reshape(-1,1),cplx.imag.reshape(-1,1)),axis=1)
    # prevs3=prevision_tableau3(tig, GR, tic, points)
    # print('\nresultat avec tableau 3',prevs3)
    # print()

    # # print()
    # # print(prevs)







    # print ('\nVERSION AVEC DATE EN DUR------------------------------------ ')
    
    # for k in range (0,5,1):
    #     dateprev_s+=3600
    #     date_prev_formate = time.strftime(" %d %b %Y %H:%M:%S ", time.gmtime(dateprev_s))
    #     vit_vent_n, angle_vent = prevision(tig, GR, dateprev_s, d[1], d[0])
    #     print('\nLe {} heure UTC Pour latitude {:6.2f} et longitude{:6.2f} '.format(date_prev_formate, d[1], d[0]))
    #     print('\tAngle du vent   {:6.1f} °'.format(angle_vent))
    #     print('\tVitesse du vent {:6.3f} Noeuds'.format(vit_vent_n))
    
    #     print()