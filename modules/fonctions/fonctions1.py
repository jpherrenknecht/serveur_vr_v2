
from scipy.interpolate import RegularGridInterpolator,interp2d,interpn
import  numpy  as np


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


# def polaire2_vect(polaires,tws,twd,HDG):
#     '''Une seule tws twd (un point) mais plusieurs caps'''
#     # on ajuste les tableaux TW et TWD à HDG
#     l=len(HDG)
#     TWD = (np.ones(l)*twd)
#     TWA = (180 - np.abs(((360 - TWD + HDG) % 360) - 180)).reshape((-1, 1))
#     TWS = (np.ones(l) * tws).reshape((-1, 1))
#     donnees = np.concatenate((TWA, TWS), axis=1)
#     # x1 et y1 sont les tableaux de vitesses de vent et de twa pour l'interpolation
#     valeurs = interpn((y1, x1), polaires, donnees, method='linear')
#     return valeurs    