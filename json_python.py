print('Essai d'aller retour avec un fichier json')

import json
from json import JSONEncoder
import numpy as np


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

     # le recharge eventuellement 
with open('static/js/barriereglaces.json', 'r') as fichier:                      # change dans fichier courants
     data2 = json.load(fichier)



print(data2['barrieretest'][1])
