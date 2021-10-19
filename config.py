import pymongo
from pymongo import MongoClient
import time
import sys
 
nombre = sys.argv[1]
# conexión
con = MongoClient('172.18.10.79',27017)
db = con.perfilSeguridad
configuracion = db.configuraciones
resultado = configuracion.find_one()

archivo = "txt/"+nombre
print(archivo)

with open(archivo, "w") as f:
    for line in resultado:
        f.write(line)
        f.write("\n")
    f.close()

   


    
   