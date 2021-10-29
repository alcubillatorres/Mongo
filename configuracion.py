
from os import stat
from sys import exit
import datetime
import sys 
import pprint
from bson.objectid import ObjectId
############### DIR IPv4 / IPv6 ############

from netaddr import *

############### DB ###############

import pymongo   
from pymongo import MongoClient
 
# conexión
#con = MongoClient('172.18.10.79',27017)
con = MongoClient('localhost',27017)

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

############### VARIABLES GLOBALES ###############

global path
global config_int_fw
global LanAvaiable
LanAvaiable = True
global LanConfLst
LanConfLst=[]
global Interfaces_Config
Interfaces_Config = []


global RouteLst
RouteLst = []

global DhcpLst
DhcpLst = []


Status1  = 'EXITOSO'
Status2  = 'NO EXITOSO'
Status_detail = ' '

maxwan = 4   ### interfaces wan maxima 4
maxlan = 10  ### interfaces lan maxima 10
maxroute = 38 ### rutas maxima 

############ Modelos de FW

fw_models = (
    #   Modelo         wan1   wan2     wan3        wan4        lan1         lan2       lan3         lan4        lan5    wan10           
    ('Fortigate 30E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 50E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 60E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 80E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 100E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 200E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 300E',('port1','port2','port3','port4','port5','port6','port7','port8','port9','port10')),
    ('Fortigate 400E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 500E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
    ('Fortigate 600E',('wan1','wan2','internal7','internal6','internal1','internal2','internal3','internal4','internal5','dmz')),
        )

########################### FUNCIONES ######################################

def saveFiles():
    global path
    path = filedialog.askdirectory(initialdir = "/",
                                          title = "Selecciona directiorio")
    
def validIP(address): 
    try:
        parts = address.split(".") 
        if len(parts) != 4: 
            return False 
        for item in parts: 
            if not 0 <= int(item) <= 255: 
                return False 
        return True
    except:
        return False

def validate_int_ipv4_wan(wan, mask, vlan, gateway, wtype_):
    vlanT=False
    vlan_v = 1
    type_v =False
    try:

        ############# VALIDAR VLAN VALIDA

        if ((vlan ==None) or (vlan==0) or (vlan==1)):
            vlanT=True
            vlan_v=1
        elif (((vlan>1) and (vlan<1002)) or ((vlan>1005) and (vlan<4094))):
            vlanT=True
            vlan_v=vlan
        else:
            vlanT=False
        
        ############# VALIDAR SI ES INTERNET

        if ((wtype_ == None) or (wtype_ =='NO') or (wtype_ == 'MPLS')):
            type_v=False
        elif ((wtype_ == 'SI') or (wtype_ == 'INTERNET')):
            type_v=True

        
        ############# VALIDAR IP VALIDA 
        ip = IPNetwork(wan)
        ip.netmask = mask

        if ((IPAddress(gateway) in IPNetwork(ip.cidr)) and (vlanT==True)):
            ipvalida= True
            #print ("Direccionamiento valido")
            Status_detail  = 'DIRECCIONAMIENTO VALIDO'
            return ipvalida,ip.ip, ip.netmask, gateway, vlan_v, type_v, Status1, Status_detail
        else: 
            #print ('Direccionamiento No Valido')
            Status_detail  = 'DIRECCIONAMIENTO NO VALIDO'
            ipvalida= False
        return ipvalida, ip.ip, mask, gateway, vlan_v, type_v,Status2, Status_detail
    except:
        #print ('Direccionamiento No Valido')
        ipvalida= False
        Status_detail  = 'DIRECCIONAMIENTO NO VALIDO'
        return ipvalida, wan, mask, gateway, vlan_v, type_v, Status2, Status_detail

def validate_int_ipv4_lan(ip, mask, vlan, dhcpsvr, dhcpinit, dhcpend,dns1,dns2):
    dns1_v='207.248.224.71'
    dns2_v='207.248.224.72'
    vlan_v=1
    statusdns1 =''
    statusdns2 =''
    
    
    try:
        ip = IPNetwork(ip)
        ip.netmask = mask
        ########## VALIDAR IP SERVER DE DHCP
        if (dns1!=0 and dns1 != None):
            if (validIP(dns1)):
                statusdns1 = '| DNS1 VALIDO | '
                #print ('DNS1 valido')
                dns1_v = dns1  
            else:
                #print ('DNS1 - No valido, se utilizara default')
                dns1_v = '207.248.224.71'
                statusdns1 = '| DNS1 NO VALIDO, SE UTILIZARA DEFAULT | '
        else:
            #print ('Se utilizara default')
            statusdns1 = '| DNS1 DEFAULT | '

        if (dns2 != 0 and dns2 != None):
            if (validIP(dns2)):
                #print ('DNS2 valido')
                statusdns2 = '| DNS2 VALIDO | '
                dns2_v = dns2
            else:
                dns2_v = '207.248.224.72'
                statusdns2 = '| DNS2 NO VALIDO, SE UTILIZARA DEFAULT | '
                #print ('DNS2 - No valido, se utilizara default')
        else:
            #print ('DNS2 - Se utilizara default')  
            statusdns2 = '| DNS2 DEFAULT | '

        

        ########## VALIDAR VLAN
        vlan = int(vlan)
        if ((vlan ==None) or (vlan==0) or (vlan==1)):
            vlanT=True
            vlan_v=1
        elif (((vlan>1) and (vlan<1002)) or ((vlan>1005) and (vlan<4094))):
            vlanT=True
            vlan_v=vlan
        else:
            vlanT=False

        ########### VALIDAR QUE DIRECCIONAMIENTO SEA VALIDO

        if (IPAddress (ip.ip) !=ip.broadcast) and (IPAddress(ip.ip) != ip.network) and(vlanT==True):
            if dhcpsvr == 'SI':
                if ((IPAddress(dhcpinit) in IPNetwork(ip.cidr)) and (IPAddress(dhcpend) in IPNetwork(ip.cidr)) and (IPAddress(dhcpinit) < IPAddress(dhcpend))and(IPAddress(dhcpinit))):                  
                    Status_detail = 'DIRECCIONAMIENTO VALIDO | DHCP VALIDO ' + statusdns1 + statusdns2
                    return True, Status1, Status_detail, ip.ip, ip.netmask, True, dhcpinit,dhcpend, dns1_v, dns2_v,vlan_v
                else:
                    Status_detail = 'DIRECCIONAMIENTO VALIDO | DHCP NO VALIDO ' + statusdns1 + statusdns2
                    return True, Status1, Status_detail, ip.ip, ip.netmask, False, dhcpinit,dhcpend, dns1_v, dns2_v,vlan_v
            else:
                Status_detail = 'DIRECCIONAMIENTO VALIDO | DHCP N/A '
                return True, Status1, Status_detail, ip.ip, ip.netmask, False, dhcpinit,dhcpend, dns1_v, dns2_v,vlan_v
        else:
            Status_detail = 'DIRECCIONAMIENTO NO VALIDO '
            return False, Status2,Status_detail, ip.ip, ip.netmask, False, dhcpinit,dhcpend, dns1_v, dns2_v,vlan_v
    except:
        Status_detail = 'DIRECCIONAMIENTO NO VALIDO '
        return False, Status2, Status_detail, ip.ip, ip.netmask, False, dhcpinit,dhcpend, dns1_v, dns2_v,vlan_v   

def config_route_ipv4(segment,mask,gateway,priority):
    global RouteLst
    global Status_detail
    port = ''
    segmentT = False
    try:
        ########### VALIDAR SINTAXIS CORRECTA DE MASK ##############
        if validIP(mask)!=True:
            Status_detail = 'MASCARA NO ES CORRECTA'
            return False,Status2,Status_detail
        
        ########### VALIDAR SINTAXIS CORRECTA DE SEGMENTO ##############

        if validIP(segment)!=True:
            Status_detail = 'SEGMENTO NO ES CORRECTO'
            return False,Status2,Status_detail
        
        ########## VALIDAR QUE SEGMENTO CORRESPONDA A LA MASCARA ###########

        ip = IPNetwork(segment)
        ip.netmask = mask
        if (segment == str(ip.network)):
            segmentT = True
            for i in range(0,len(Interfaces_Config)):
                listint = IPNetwork(Interfaces_Config[i][3])
                listint.netmask = Interfaces_Config[i][4]
                if ((IPAddress(gateway) in IPNetwork(listint.cidr))):
                    with open(config_int_fw, 'a') as f:
                        #f.write("config router static\n")
                        f.write("   edit 0\n")
                        f.write("       set gateway {}\n".format(gateway))
                        f.write("       set device \"{}\"\n".format(Interfaces_Config[i][1]))
                        f.write("       set dst {} {}\n".format(ip.network,ip.netmask))
                        f.write("       set priority {}\n".format(priority))
                        f.write("   next\n")
                        #f.write("end\n")
                    Status_detail = 'INFORMACION DE RUTEO CORRECTA'
                    RouteLst.append([segment,mask,gateway,priority])
                    return True, Status1,Status_detail
                else:
                    #print ('ruta no valida')
                    Status_detail = 'NO EXISTE UNA INTERFACE HACIA EL GATEWAY PROPORCIONADO'
            return False, Status2,Status_detail            
        else:
            #print (f'segmento: {segment}, no corresponde a la mascara ingresada: {mask} segmento debería ser: {ip.network}')
            Status_detail = 'SEGMENTO NO ES CORRECTO'
            return False,Status2,Status_detail

        ###################### CONFIGURACION DE RUTAS ######################
        
    except:
        Status_detail = 'INFORMACION DE RUTEO INCORRECTA'
        return False,Status2,Status_detail, port

def config_int_ipv4_wan_dot1q(port, mode_ip,alias, ip, mask,gateway, vlan,internet):
    global Status_detail 
    nameint = port
 
    try:
        with open(config_int_fw, 'a') as f:
        # if (port !=0 and port!=None)and (mode_ip !=0 and mode_ip!=None)and(alias !=0 and alias!=None)and(ip !=0 and ip!=None)and(mask !=0 and mask!=None):
            if vlan == 1:
                #f.write("config system interface\n")
                if mode_ip == "MANUAL":
                        #print ("TEST1 = static, vlan 1 o None")
                        f.write("   edit \"{}\"\n".format(port))
                        f.write("      set vdom \"root\"\n")
                        f.write("       set ip {} {}'\n".format(ip, mask))
                        f.write("       set allowaccess ping https ssh snmp http\n")
                        f.write("       set type physical\n")
                        f.write("       set alias {}\n".format(alias))
                        f.write("       set role wan\n")
                        f.write("   next\n")
                        return True, Status1, Status_detail,nameint
                        #f.write("end\n")
                        '''---- >>> SE QUITA PARA CONFIGURAR SDWAN 
                        if (internet ==True):
                            f.write("config router static\n")
                            f.write("   edit 0\n")
                            f.write("       set gateway {}\n".format(gateway))
                            f.write("       set device \"{}\"\n".format(port))
                            f.write("       set dst 0.0.0.0\n")
                            f.write("   next\n")
                            #f.write("end\n")
                            return True, Status1, Status_detail, nameint
                        else:
                            return True, Status1, Status_detail, nameint
                            '''
                elif mode_ip == "DHCP":
                        #print ("TEST2 = dhcp, vlan 1 o None")
                        f.write("   edit \"{}\"\n".format(port))
                        f.write("       set vdom \"root\"\n")
                        f.write("       set mode dhcp\n")
                        f.write("       set allowaccess ping https ssh snmp http\n")
                        f.write("       set type physical\n")
                        f.write("       set alias {}\n".format(alias))
                        f.write("       set role wan\n")
                        f.write("   next\n")
                        #f.write("end\n")
                        return True, Status1, Status_detail,nameint
                else:
                    #Configuración de PPoE pendiente.
                    Status_detail = "FUNCION PPoE NO IMPLEMENTADA"
                    return False, Status2, Status_detail,nameint
            else:
                #f.write("config system interface\n")
                nameint = alias
                if mode_ip == "MANUAL":
                        #print ("TEST3 = static, vlan X")
                        f.write("   edit \"{}\"\n".format(alias))
                        f.write("       set vdom \"root\"\n")
                        f.write("       set ip {} {}'\n".format(ip, mask))
                        f.write("       set allowaccess ping https ssh snmp http\n")
                        f.write("       set alias \"{}\"\n".format(alias))
                        f.write("       set interface {}\n".format(port))
                        f.write("       set vlanid {}\n".format(vlan))
                        f.write("   next\n")
                        return True, Status1, Status_detail,nameint
                        #f.write("end\n")
                        '''---- >>> SE QUITA PARA CONFIGURAR SDWAN 
                        if internet ==True:
                            f.write("config router static\n")
                            f.write("   edit 0\n")
                            f.write("       set gateway {}\n".format(gateway))
                            f.write("       set device \"{}\"\n".format(alias))
                            f.write("       set dst 0.0.0.0\n")
                            f.write("   next\n")
                            #f.write("end\n")
                            return True, Status1, Status_detail,nameint
                        else:
                            return True, Status1, Status_detail,nameint
                        '''
                elif mode_ip == "DHCP":
                        #print ("TEST4 = dhcp, vlan x")
                        f.write("   edit \"{}\"\n".format(alias))
                        f.write("       set vdom \"root\"\n")
                        f.write("       set mode dhcp\n")
                        f.write("       set allowaccess ping https ssh snmp http\n")
                        f.write("       set alias \"{}\"\n".format(alias))
                        f.write("       set interface {}\n".format(port))
                        f.write("       set vlanid {}\n".format(vlan))
                        f.write("   next\n")
                        #f.write("end\n")
                        return True, Status1, Status_detail,nameint
                else:
                    #Configuración de PPoE no aplica con VLAN
                    Status_detail = "FUNCION PPoE NO PUEDE UTILIZAR VLAN"
                    return False, Status2, Status_detail, nameint
            return True, Status1, Status_detail
    except:
        Status_detail = 'ERROR EN EJECUCION DE PROGRAMA'
        return False,Status2, Status_detail,nameint

def config_int_ipv4_lan_dot1q(port,alias, ip, mask, dhcpsvr, vlan,dhcpinit,dhcpend,dns1,dns2):
    global Status_detail 
    global LanConfLst
    global LanAvaiable
    global DhcpLst
    nameint =port
       
    try:
        with open(config_int_fw, 'a') as f:  
        # if (port !=0 and port!=None)and (mode_ip !=0 and mode_ip!=None)and(alias !=0 and alias!=None)and(ip !=0 and ip!=None)and(mask !=0 and mask!=None):
            if LanAvaiable==True:
                if vlan ==1:   
                    LanAvaiable = False
                    #f.write("config system interface\n")    
                    f.write("   edit \"{}\"\n".format(port))
                    f.write("      set vdom \"root\"\n")
                    f.write("       set ip {} {}'\n".format(ip, mask))
                    f.write("       set allowaccess ping https ssh snmp http\n")
                    f.write("       set type physical\n")
                    f.write("       set alias {}\n".format(alias))
                    f.write("       set role lan\n")
                    f.write("   next\n")
                    #f.write("end\n")
                    
                    if dhcpsvr == True:
                        DhcpLst.append([ip,mask,port,dns1,dns2,dhcpinit,dhcpend])
                    '''
                        #f.write("config system dhcp server\n")
                        f.write("   edit 0\n")
                        f.write("       set vdom ntp-service local\n")
                        f.write("       set default-gateway {}\n".format(ip))
                        f.write("       set netmask {}\n".format(mask))
                        f.write("       set interface {}\n".format(port))
                        f.write("       set dns-server1 {}\n".format(dns1))
                        f.write("       set dns-server2 {}\n".format(dns2))
                        f.write("       config ip-range\n")
                        f.write("           edit 1\n")
                        f.write("               set start-ip {}\n".format(dhcpinit))
                        f.write("               set end-ip {}\n".format(dhcpend))
                        f.write("           next\n")
                        f.write("       end\n")
                        f.write("   next\n")
                        f.write("end\n")
                        return True, Status1, Status_detail,nameint
                    '''
                    return True, Status1, Status_detail,nameint
                else:
                    nameint=alias
                    #f.write("config system interface\n")    
                    f.write("   edit \"{}\"\n".format(alias))
                    f.write("       set vdom \"root\"\n")
                    f.write("       set ip {} {}\n".format(ip, mask))
                    f.write("       set allowaccess ping https ssh snmp http\n")
                    f.write("       set alias Vlan{}\n".format(vlan))
                    f.write("       set role lan\n")
                    f.write("       set interface {}\n".format(port))
                    f.write("       set vlanid {}\n".format(vlan))
                    f.write("   next\n")
                    #f.write("end\n")
                    
                    if dhcpsvr == True:
                        DhcpLst.append([ip,mask,port,dns1,dns2,dhcpinit,dhcpend])
                    '''
                        #f.write("config system dhcp server\n")
                        f.write("   edit 0\n")
                        f.write("       set vdom ntp-service local\n")
                        f.write("       set default-gateway {}\n".format(ip))
                        f.write("       set netmask {}\n".format(mask))
                        f.write("       set interface {}\n".format(alias))
                        f.write("       set dns-server1 {}\n".format(dns1))
                        f.write("       set dns-server2 {}\n".format(dns2))
                        f.write("       config ip-range\n")
                        f.write("           edit 1\n")
                        f.write("               set start-ip {}\n".format(dhcpinit))
                        f.write("               set end-ip {}\n".format(dhcpend))
                        f.write("           next\n")
                        f.write("       end\n")
                        f.write("   next\n")
                        f.write("end\n")
                        return True, Status1, Status_detail,nameint
                    '''
                    return True, Status1, Status_detail,nameint
            else:
                if vlan ==1:
                    #print ('Error vlan 1 ya se encuentra configurada')
                    Status_detail = 'VLAN 1 YA SE ENCUENTRA CONFIGURADA'
                    return False, Status2, Status_detail,nameint
                else:
                    nameint=alias
                    #f.write("config system interface\n")    
                    f.write("   edit \"{}\"\n".format(alias))
                    f.write("       set vdom \"root\"\n")
                    f.write("       set ip {} {}'\n".format(ip, mask))
                    f.write("       set allowaccess ping https ssh snmp http\n")
                    f.write("       set alias Vlan{}\n".format(vlan))
                    f.write("       set role lan\n")
                    f.write("       set interface {}\n".format(port))
                    f.write("       set vlanid {}\n".format(vlan))
                    f.write("   next\n")
                    #f.write("end\n")
                    if dhcpsvr == True:
                        DhcpLst.append([ip,mask,port,dns1,dns2,dhcpinit,dhcpend])
                    '''
                        #f.write("config system dhcp server\n")
                        f.write("   edit 0\n")
                        f.write("       set vdom ntp-service local\n")
                        f.write("       set default-gateway {}\n".format(ip))
                        f.write("       set netmask {}\n".format(mask))
                        f.write("       set interface {}\n".format(alias))
                        f.write("       set dns-server1 {}\n".format(dns1))
                        f.write("       set dns-server2 {}\n".format(dns2))
                        f.write("       config ip-range\n")
                        f.write("           edit 1\n")
                        f.write("               set start-ip {}\n".format(dhcpinit))
                        f.write("               set end-ip {}\n".format(dhcpend))
                        f.write("           next\n")
                        f.write("       end\n")
                        f.write("   next\n")
                        f.write("end\n")
                        return True, Status1, Status_detail,nameint
                    '''
                    return True, Status1, Status_detail,nameint
            
    except:
        Status_detail = 'ERROR EN EJECUCION DE PROGRAMA'
        return False, Status2, Status_detail,nameint                   

def config_dhcp(gateway,mask,port,dns1,dns2,dhcpinit,dhcpend):
    global Status_detail 
    try:
        with open(config_int_fw, 'a') as f: 
            
            #f.write("config system dhcp server\n")
            f.write("   edit 0\n")
            f.write("       set vdom ntp-service local\n")
            f.write("       set default-gateway {}\n".format(gateway))
            f.write("       set netmask {}\n".format(mask))
            f.write("       set interface {}\n".format(port))
            f.write("       set dns-server1 {}\n".format(dns1))
            f.write("       set dns-server2 {}\n".format(dns2))
            f.write("       config ip-range\n")
            f.write("           edit 1\n")
            f.write("               set start-ip {}\n".format(dhcpinit))
            f.write("               set end-ip {}\n".format(dhcpend))
            f.write("           next\n")
            f.write("       end\n")
            f.write("   next\n")
            f.write("end\n")
            Status_detail = "EXITOSO"
            return True, Status1, Status_detail
    except:
        Status_detail = 'INFORMACIÓN DE DHCP NO VALIDA'
        return False, Status2, Status_detail

def config_dnat():
    pass

    '''
    config firewall ippool
        edit "201.151.147.151"
            set startip 201.151.147.151
            set endip 201.151.147.151
        next
        edit "201.151.147.146"
            set startip 201.151.147.146
            set endip 201.151.147.146
        next
    end
    config firewall vip
        edit "Avaya"
            set uuid 5e76ed08-92bf-51eb-e43b-482847337fb2
            set extip 201.151.147.146
            set extintf "wan1"
            set mappedip "192.168.50.2"
        next
    end
    '''

def config_snat():
    pass

def config_snmp(hostname = "hostname_FW"):
    global Status_detail 
    global config_int_fw
    try:
        with open(config_int_fw, 'a') as f:  
            f.write("config system snmp sysinfo\n")
            f.write("   set status enable\n")
            f.write("   set description \"{}\"\n".format(hostname))
            f.write("   set contact-info \"Alestra SOC\"\n")
            f.write("   set location \"OSS\"\n")
            f.write("   end\n")
            f.write("config system snmp community\n")
            f.write("   edit 1\n")
            f.write("       set name \"009511995\"\n")
            f.write("       config hosts\n")
            f.write("           edit 1\n")
            f.write("               set ip 201.163.54.0 255.255.255.0\n")
            f.write("           next\n")
            f.write("           edit 2\n")
            f.write("               set ip 189.206.239.0 255.255.255.0\n")
            f.write("           next\n")
            f.write("           edit 3\n")
            f.write("               set ip 189.206.238.0 255.255.255.0\n")
            f.write("           next\n")
            f.write("       end\n")
            f.write("   next\n")
            f.write("end\n")
            Status_detail = "EXITOSO"
            return True, Status1, Status_detail
    except:
        Status_detail = 'INFORMACIÓN DE SNMP NO VALIDA'
        return False, Status2, Status_detail

def config_users():
    global Status_detail 
    global config_int_fw
    try:
        with open(config_int_fw, 'a') as f:  
            f.write("config system admin\n")
            f.write("   edit \"admin\"\n")
            f.write("       set accprofile \"super_admin\"\n")
            f.write("       set vdom \"root\"\n")
            f.write("       set password ENC SH2AYPAjcjaXZL0WNEFCpPLF9Vbm7bCdyLq6XU/ApUstInRwCn1N7M9PJ0epQw=\n")
            f.write("       next\n")
            f.write("   edit \"entregas\"\n")
            f.write("       set accprofile \"super_admin\"\n")
            f.write("       set vdom \"root\"\n")
            f.write("       set password ENC SH24+IQDCra5DPtl6jv01V9M/q2RaTw6039nF9BKgLN7a9/eQbxURwAr4/Qobg=\n")
            f.write("       next\n")
            f.write("   edit \"soc_alestra\"\n")
            f.write("       set accprofile \"super_admin\"\n")
            f.write("       set vdom \"root\"\n")
            f.write("       set password ENC SH2YBPm22W72oBuKyEyVCSBJVVQU2ntDFi4iqOFNXSpOGDWTQ75SCK0Z+3EM68=\n")
            f.write("       next\n")
            f.write("   end\n")
            Status_detail = "EXITOSO"
            return True, Status1, Status_detail
    except:
        Status_detail = 'INFORMACIÓN DE USUARIOS VALIDA'
        return False, Status2, Status_detail
  
def main():
    try:
        global DhcpLst
        global config_int_fw

        #*****************INICIO DE PROGRAMA

        customer_os = "Sistema"
        customer_key = sys.argv[5]
        customer_name = sys.argv[3]
        customer_site = sys.argv[2]
        fmodel = sys.argv[4]
        config_int_fw =  f'txt/ARCHIVO_DE_CONFIG_{sys.argv[1]}'
        status_file = f'txt/REPORTE_DE_CONFIG__{sys.argv[1]}'

        resultado = configuracion.find_one({"Id_Sitio": ObjectId(customer_site)})

        with open(config_int_fw,'w') as f:
            f.write("config system interface\n")
            f.close()
            
            with open(status_file,'w') as sf:
                sf.write(f'REPORTE DE CONFIGURACION'.rjust(60))
                sf.write(f'\n\nCLIENTE: {customer_name}\nOS: {customer_os}\nLLAVE: {customer_key}\nSITE: {customer_site}\nFECHA: {datetime.date.today()}\n\n')
            

                for mod in range(0, len(fw_models)):
                    if fw_models[mod][0]==str(fmodel):
                        interfaces = fw_models[mod][1]
                        
                ####### CONFIG INTERFACES WAN ############

                print ('********************************** CONFIGURACIÓN DE INTERFACES WAN **********************************\n')
                sf.write('********************************** CONFIGURACIÓN DE INTERFACES WAN **********************************\n')

                ############# OBTENER WAN DE MONGO #####################

                for w in range(0,len(resultado['Wan']),1):
                    wdesc = resultado['Wan'][w]['Alias']
                    wmode = resultado['Wan'][w]['TipoIP']
                    wtype = resultado['Wan'][w]['TipoServicio']
                    wwanip = resultado['Wan'][w]['DireccionIP']
                    wmask = resultado['Wan'][w]['Mascara']
                    wgateway = resultado['Wan'][w]['Gateway']
                    wvlan = int(resultado['Wan'][w]['Vlan'])

                    if ((wdesc !=0 and wdesc!=None) and (wtype !=0 and wtype!=None) and (wmode !=0 and wmode!=None) and (wwanip !=0 and wwanip!=None) and (wmask !=0 and wmask!=None) and (wgateway !=0 and wgateway!=None)):
                        wan_ip = validate_int_ipv4_wan(wan=wwanip, mask=wmask, vlan=wvlan, gateway=wgateway, wtype_ =wtype)

                        print(wan_ip)
                        if wan_ip[0] == True:
                            print (f'INTERFACE WAN{w+1}')
                            print (f'VALIDACION DE INFORMACION: {wan_ip[6]}')
                            sf.write(f'\nINTERFACE WAN{w+1}\n')
                            sf.write(f'VALIDACION DE INFORMACION: {wan_ip[6]}\n')
                            config_wan = config_int_ipv4_wan_dot1q(port=interfaces[w],mode_ip=wmode, alias=wdesc,ip=wan_ip[1], mask=wan_ip[2], gateway=wan_ip[3],vlan=wan_ip[4], internet=wan_ip[5])

                            if config_wan[0] == True:
                                Interfaces_Config.append(["WAN", config_wan[3],wdesc, wwanip,wmask])
                                print (f'STATUS DE CONFIGURACION: {config_wan[1]}\n')
                                sf.write(f'STATUS DE CONFIGURACION: {config_wan[1]}\n')
                            else:
                                print (f'STATUS DE CONFIGURACION: {config_wan[1]}')
                                print (f'DETALLE DE CONFIGURACION: {config_wan[2]}\n')
                                sf.write(f'STATUS DE CONFIGURACION: {config_wan[1]}')
                                sf.write(f'DETALLE DE CONFIGURACION: {config_wan[2]}\n')
                        else: 
                            print (f'INTERFACE WAN{w+1}')
                            print (f'VALIDACION DE INFORMACION: {wan_ip[6]}')
                            print (f'DETALLE: {wan_ip[7]}\n')
                            sf.write(f'\nINTERFACE WAN{w+1}\n')
                            sf.write(f'VALIDACION DE INFORMACION: {wan_ip[6]}\n')
                            sf.write(f'DETALLE: {wan_ip[7]}\n')
                               
                ####### CONFIG INTERFACES LAN #############
                
                print (f'********************************** CONFIGURACIÓN DE INTERFACES LAN **********************************\n')
                sf.write('\n********************************** CONFIGURACIÓN DE INTERFACES LAN **********************************\n\n')


                ############# OBTENER LAN DE MONGO #####################

                for l in range(0,len(resultado['Lan']),1):
                    ldesc = resultado['Lan'][l]['LanAlias']
                    #lport = fw.loc[:,'id_lint'][l]
                    lip = resultado['Lan'][l]['LanDireccionIP']
                    lmask = resultado['Lan'][l]['LanMascara']
                    lvlan = resultado['Lan'][l]['LanVlan'] 
                    ldhcp_svr_en = resultado['Lan'][l]['LanDHCP'] 
                    ldhcp_init = resultado['Lan'][l]['DHCPFrom']  
                    ldhcp_end = resultado['Lan'][l]['DHCPTo']  
                    ldns1 = resultado['Lan'][l]['LanServidorDNS1']     
                    ldns2 = resultado['Lan'][l]['LanServidorDNS2']

                   
                    if (ldesc !=0 and ldesc!=None)and(lip !=0 and lip!=None)and(lmask !=0 and lmask!=None):
                        lan_ip= validate_int_ipv4_lan(ip=lip, mask=lmask, dhcpsvr=ldhcp_svr_en, vlan=lvlan, dhcpinit=ldhcp_init, dhcpend=ldhcp_end, dns1=ldns1, dns2=ldns2)

                        print (f'INTERFACE LAN{l+1}')
                        print (f'VALIDACION DE INFORMACION: {lan_ip[1]}')
                        print (f'DETALLE DE VALIDACION: {lan_ip[2]}')

                        sf.write(f'\nINTERFACE LAN{l+1}\n')
                        sf.write(f'VALIDACION DE INFORMACION: {lan_ip[1]}\n')
                        sf.write(f'DETALLE DE VALIDACION: {lan_ip[2]}\n')
                        
                        if lan_ip[0]==True:

                            config_lan=config_int_ipv4_lan_dot1q(port=interfaces[4],alias=ldesc,ip=lan_ip[3], mask=lan_ip[4], dhcpsvr=lan_ip[5],vlan=lan_ip[10], dhcpinit=lan_ip[6],dhcpend=lan_ip[7],dns1=lan_ip[8],dns2=lan_ip[9])
                            
                            if config_lan[0] == True:
                                print (f'STATUS DE CONFIGURACION: {config_lan[1]}\n')
                                Interfaces_Config.append(["LAN", config_lan[3],ldesc, str(lan_ip[3]),str(lan_ip[4])])
                                sf.write(f'STATUS DE CONFIGURACION: {config_lan[1]}\n')
                            else:
                                print (f'STATUS DE CONFIGURACION: {config_lan[1]}')
                                print (f'DETALLE DE CONFIGURACION: {config_lan[2]}\n')
                                sf.write(f'STATUS DE CONFIGURACION: {config_lan[1]}\n')
                                sf.write(f'DETALLE DE CONFIGURACION: {config_lan[2]}\n')
                        else:
                            print (f'STATUS DE CONFIGURACION: NO EXITOSO')
                            print (f'DETALLE DE CONFIGURACION: DIRECCIONAMIENTO INCORRECTO\n')
                            sf.write(f'STATUS DE CONFIGURACION: NO EXITOSO\n')
                            sf.write(f'DETALLE DE CONFIGURACION: DIRECCIONAMIENTO INCORRECTO\n')
                            
                    #else:
                    #    print (f'Interface {i} Información incompleta')

                
                with open(config_int_fw,'a') as f:
                    f.write("end\n")
                    f.write("config router static\n")
                    f.close()  

                
                ####### CONFIG DE RUTAS #############

                print ('********************************** CONFIGURACIÓN DE RUTEO **********************************\n')
                sf.write('\n********************************** CONFIGURACIÓN DE RUTEO **********************************\n\n')
                
                ############# OBTENER RUTAS DE MONGO #####################

                for i in range(0,(len(resultado['Rutas'])),1):
                    rsegment = resultado['Rutas'][i]['Red']
                    rmask = resultado['Rutas'][i]['Mascara']
                    rgarteway = resultado['Rutas'][i]['Gateway']
                    rpriority = resultado['Rutas'][i]['Prioridad']
                    rdefault = resultado['Rutas'][i]['Default']   
                    if (rsegment !=0 and rsegment!=None)and(rmask !=0 and rmask!=None)and(rgarteway !=0 and rgarteway!=None)and(rpriority !=0 and rpriority!=None):
                        
                        route = config_route_ipv4(rsegment,rmask,rgarteway,rpriority)

                        print (f'RUTA {i+1}')
                        print (f'SEGMENTO: {rsegment}')
                        print (f'MASCARA: {rmask}')
                        print (f'GATEWAY: {rgarteway}')
                        sf.write(f'\nRUTA{i+1}\n')
                        sf.write(f'SEGMENTO: {rsegment}\n')
                        sf.write(f'MASCARA: {rmask}\n')
                        sf.write(f'GATEWAY: {rgarteway}\n')

                        if route[0] ==True:
                            print (f'STATUS DE CONFIGURACION: {route[1]}')
                            print (f'DETALLE DE CONFIGURACION: {route[2]}\n')
                            sf.write(f'STATUS DE CONFIGURACION: {route[1]}\n')
                        else:
                            print (f'STATUS DE CONFIGURACION: {route[1]}')
                            print (f'DETALLE DE CONFIGURACION: {route[2]}\n')
                            sf.write(f'STATUS DE CONFIGURACION: {route[1]}\n')
                            sf.write(f'DETALLE DE CONFIGURACION: {route[2]}\n')
                
                with open(config_int_fw,'a') as f:
                    f.write("end\n")
                    f.write("config system dhcp server\n")
                
                print ('********************************** CONFIGURACIÓN DE DHCP SERVER **********************************\n')
                sf.write('\n********************************** CONFIGURACIÓN DHCP SERVER **********************************\n\n')
  
                for d in range(0,(len(DhcpLst)),1):
                    dhcp = config_dhcp(gateway = DhcpLst[d][0],mask = DhcpLst[d][1],port = DhcpLst[d][2],dns1= DhcpLst[d][3],dns2= DhcpLst[d][4],dhcpinit=DhcpLst[d][5],dhcpend=DhcpLst[d][6])
                    if dhcp[0] ==True:
                            print (f'STATUS DE CONFIGURACION: {dhcp[1]}')
                            print (f'DETALLE DE CONFIGURACION: {dhcp[2]}\n')
                            sf.write(f'STATUS DE CONFIGURACION: {dhcp[1]}\n')
                    else:
                        print (f'STATUS DE CONFIGURACION: {dhcp[1]}')
                        print (f'DETALLE DE CONFIGURACION: {dhcp[2]}\n')
                        sf.write(f'STATUS DE CONFIGURACION: {dhcp[1]}\n')
                        sf.write(f'DETALLE DE CONFIGURACION: {dhcp[2]}\n')
            
                with open(config_int_fw,'a') as f:
                    #f.write("end\n")
                    f.close()    
            
                print ('********************************** CONFIGURACIÓN DE SNMP **********************************\n')
                sf.write('\n********************************** CONFIGURACIÓN SNMP **********************************\n\n')
                
                snmp = config_snmp()
                if snmp[0] ==True:
                    print (f'STATUS DE CONFIGURACION: {snmp[1]}')
                    print (f'DETALLE DE CONFIGURACION: {snmp[2]}\n')
                    sf.write(f'STATUS DE CONFIGURACION: {snmp[1]}\n')
                else:
                    print (f'STATUS DE CONFIGURACION: {snmp[1]}')
                    print (f'DETALLE DE CONFIGURACION: {snmp[2]}\n')
                    sf.write(f'STATUS DE CONFIGURACION: {snmp[1]}\n')
                    sf.write(f'DETALLE DE CONFIGURACION: {snmp[2]}\n')
                print ('********************************** CONFIGURACIÓN DE USUARIOS **********************************\n')
                sf.write('\n********************************** CONFIGURACIÓN USUARIOS **********************************\n\n')
                
                users = config_users()
                if users[0] ==True:
                    print (f'STATUS DE CONFIGURACION: {users[1]}')
                    print (f'DETALLE DE CONFIGURACION: {users[2]}\n')
                    sf.write(f'STATUS DE CONFIGURACION: {users[1]}\n')
                else:
                    print (f'STATUS DE CONFIGURACION: {users[1]}')
                    print (f'DETALLE DE CONFIGURACION: {users[2]}\n')
                    sf.write(f'STATUS DE CONFIGURACION: {users[1]}\n')
                    sf.write(f'DETALLE DE CONFIGURACION: {users[2]}\n')
                ##sf.close()

                '''pruebas - para validar lista de interfaces creadas.

                print (Interfaces_Config)
                for w in range(0,len(resultado['Wan']),1):
                    print (resultado['Wan'][w]['Alias'])
                    interface = resultado['Wan'][w]
                '''
                
    except:
        pass
    pass

############################## MAIN ########################################

if __name__ == '__main__':
   main()
