
from os import stat
from sys import exit
import sys 
from bson.objectid import ObjectId

############### DIR IPv4 / IPv6 ############

from netaddr import *

############### DB ###############

import pymongo   
from pymongo import MongoClient
 
# conexión
con = MongoClient('172.18.10.79',27017)
#con = MongoClient('localhost',27017)

#base de datos
db = con.perfilSeguridad
 
# colección
configuracion= db.configuraciones


############### APP EXE ##########################
import tkinter
from tkinter import messagebox
#from tkinter.constants import *
from tkinter.font import Font 
from tkinter import filedialog
from tkinter import PhotoImage
from PIL import ImageTk, Image
from typing import Collection, Sized


 
fileName = sys.argv[1]
Id_Sitio = sys.argv[2]
NombreCliente = sys.argv[3]
Modelo = sys.argv[4]
Key = sys.argv[5]


resultado = configuracion.find_one({"Id_Sitio": ObjectId(Id_Sitio)})

archivo = "txt/"+fileName

customer_os = "SO"
customer_key = Key
customer_name = NombreCliente
customer_site = Id_Sitio
fmodel = Modelo

with open(archivo, "w") as f:
    for line in resultado:
        f.write(line)
        f.write("\n")
    f.write(Id_Sitio)
    f.write("\n")
    f.write(NombreCliente)
    f.write("\n")
    f.write(Modelo)
    f.write("\n")
    f.write(Key)
    f.close()

   


    
   