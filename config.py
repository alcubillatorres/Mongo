import pymongo
 
from pymongo import MongoClient
import time
from datetime import datetime
 
# conexión
con = MongoClient('localhost',27017)
#base de datos
db = con.perfilSeguridad
 
# colección
configuracion = db.configuraciones
clientes = db.clientes
sitios = db.sitios

resultado = configuracion.find_one()

Cliente = clientes.find_one({'Nombre' : 'Cliente 2'})
idCliente = str(Cliente['_id'])


Sitio = sitios.find_one({'Cliente_id' : idCliente})
Llave = Sitio['Key']
fecha = datetime.now().strftime("%Y%m%d%H%M%S")

nombre = "txt/configuracion_"+idCliente+'_'+Llave+'_'+fecha+".txt"


with open(nombre, "w") as f:
    for line in resultado:
        f.write(line)
        f.write("\n")
    f.close()
    time.sleep(5)

   


    
   