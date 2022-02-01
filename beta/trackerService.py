##################################################################################
#Proyecto: trackerService					                                     #
#Autor: Yggdrassil80			                                         #
#Descricpión: Servicio de tracker experimental para el seguimiento mendiante una #
#  antena autoapuntada contra el HAB, implica disoner de GPS integrado y una MPU.#
#  Además de una plataforma mobil con dos ejes de libertad. De momento los       #
#  actuadores serian servos convencionales. No motores paso a paso               #
##################################################################################
from pyorbital import orbital

import numpy as np
from datetime import datetime 
import ConfigHelper
import logging

#Creacion del logger del tracker
logger = logging.getLogger('server_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('/data/hab_antena/logs/tracker.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s|%(message)s|', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)

ACTIVO = 1
NO_ACTIVO = 0
GPS_DATA_LOG_FILE = "/data/hab_antena/logs/gpsdata.log"

posAntena = ConfigHelper.getPosAntena()
gps_activo = ConfigHelper.isGPSActivo()
ori_activo = ConfigHelper.isORIActivo()
mpu_activo = ConfigHelper.isMPUActivo()
tiempoEntreMov = ConfigHelper.getTiempoEntreMov()

#Procedure that returns antenna position (lat, lon, alt)
def recuperarPosAntena():
    #1. La posicion de la antena se ha de recuperar de un GPS que este embebido dentro del sistema de la sonda.
    #Se asume que la posicion GPS se almacena en el archivo del servicio de GPS. /data/hab_antena/logs/gpsdata.log
    #Si la señal GPS se pierde o hay un error, siempre se cogera la ultima posición generada en este archivo como valida.
    with open(GPS_DATA_LOG_FILE) as gpsdatafile:
        line = list(gpsdatafile)[-1]
    
    return [0.0, 0.0, 0]

#Procedure that returns sat, hab or other kind of vehicle position (lat, log, alt) 
def recuperarPosSonda():
    return [0.0, 0.0, 0]

#Procedure that returns azimuth and elevation angles based on antena and vehicle positions
def calcularAzEl(posAntena, posSonda):

    azi = 0.0
    elev = 0.0

    try:

        logger.info("[calcularAzEl][ini]")
        t = datetime(2018, 1, 1, 0, 0, 0)
        sat_lon = np.array([[posSonda[0],0.1],[0.1,0.1]])
        sat_lat = np.array([[posSonda[1],0.1],[0.1,0.1]])
        sat_alt = np.array([[posSonda[2],1],[1,1]])
        lon = np.array([[posAntena[0],0.1],[0.1,0.1]])
        lat = np.array([[posAntena[1],0.1],[0.1,0.1]])
        alt = posAntena[2]

        azi, elev = orbital.get_observer_look(sat_lon, sat_lat, sat_alt, t, lon, lat, alt)
        logger.debug("[calcularAzEl][azi: " + str(azi) + " elev: " + str(elev) + "]")
        logger.info("[calcularAzEl][fin]")
    except:
        logger.error("[calcularAzEl][ERROR]")
    return azi, elev

def estabilizarPlataformaAntena():
    logger.info("[platformEstabilizer][Estabilizando Plataforma...]")
    logger.info("[platformEstabilizer][Plataforma Estabilizada!]")

def moverAntena(az,el,err):
    logger.info("[moverAntena][Moviendo la antena...]")
    logger.info("[moverAntena][Antena en posicion!]")

def recuperarDatosBrujula():
    return 0.0

try:

    logger.log("[trackerService][Starting tracker...]")
    orientacionAntena = 0.0
    azUpt = 0.0
    elUpt = 0.0

    while True:

        if gps_activo == ACTIVO:
           #1. Recuperar datos de gps de la posicion de la antena
           logger.debug("[trackerService][GPS Active]")
           posAntena = recuperarPosAntena()
           logger.debug("[trackerService][posAntena recovered by GPS: lat: " + posAntena[0] + " lon: " + posAntena[1] + " alt: " + posAntena[2])
        #2. Recuperar posicion Sonda
        posSonda = recuperarPosSonda()
        logger.debug("[trackerService][posSonda recovered lat: " + posSonda[0] + " lon: " + posSonda[1] + " alt: " + posSonda[2])
        #3. Calcular az y el
        az,el = calcularAzEl(posAntena, posSonda)
        #4. recuperar si el sistema de tracking esta activo dentro del bucle, porque cambiando
        #la configuracion en caliente, se podria activar o desactivar 
        
        if mpu_activo == ACTIVO:
            #4.1 Si el mpu esta activo, recuperar la información del giroscopio para calcular los errores de azimut y elevacion que la 
            #disposicion de la plataforma donde esta la antena esta generando.
            logger.debug("[trackerService][MPU active, using info to generate az and el corrections")
            azUpt, elUpt = calcularErrorAzElPlataforma()
            logger.debug("[trackerService][azUpt: " + str(azUpt) + " elUpt: " + str(elUpt) + "]")
        
        if ori_activo == ACTIVO:
            #4.2 Si la brujula esta activa, usar los datos para calcular bien el azimut
            logger.debug("[trackerService][compass active, recovering data to generate az corrections]")
            orientacionAntena = recuperarDatosBrujula()
            logger.debug("[trackerService][compass degress: " + orientacionAntena + ]")
        
        logger.debug("[trackerService][Reorienting antenna...]")
        moverAntena(az,el,orientacionAntena, azUpt, elUpt)
        logger.debug("[trackerService][Antenna oriented correctly]]")
        sleep(tiempoEntreMov)

except:
    print("[ERROR] Se sigue interando...")

