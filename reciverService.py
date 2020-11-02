##################################################################################
#Proyecto: trackerService					                                     #
#Autor: Oscar Loras Delgado				                                         #
#Descricpión: Servicio de tracker experimental para el seguimiento mendiante una #
#  antena autoapuntada contra el HAB, implica disoner de GPS integrado y una MPU.#
#  Además de una plataforma mobil con dos ejes de libertad. De momento los       #
#  actuadores serian servos convencionales. No motores paso a paso               #
##################################################################################

import os
import glob
import serial
import time
import datetime
import binascii
import logging

import GPSHelper
import ConfigHelper

#Creacion del logger para los logs del servicio
loggerLog = logging.getLogger('server_logger')
loggerLog.setLevel(logging.DEBUG)
inf = logging.FileHandler('/data/hab_antena/logs/reciverService.log')
inf.setLevel(logging.DEBUG)
formatterInformer = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]', datefmt='%Y-%m-%d %H:%M:%S')
inf.setFormatter(formatterInformer)
loggerLog.addHandler(inf)

usbRF = ConfigHelper.getUsbRF()
loggerLog.info("[ReciverService][Conf] Puerto USB RF: " + usbRF);

#puertoUSB=serial.Serial('/dev/ttyUSB0',baudrate=9600, timeout = 5.0)
#puertoUSB=serial.Serial('COM4', baudrate=115200, timeout = 5.0)
puertoUSB=serial.Serial(usbRF)
#puertoUSB=serial.Serial('COM4', timeout = 5.0)
#puertoUSB=serial.Serial('COM4')

#C1C1C1 deberia devolver      C 0  0 0  0 0  1 A  1 7  4 4
#                            6330 3030 3030 3161 3137 3434
#key = ''.join(chr(x) for x in [0xC1, 0xC1, 0xC1])
#print ("key: " + st

#Archivo donde almacenaran los datos recibidos
LOG_PATH = "/data/hab_antena/logs/recivedData.log"

recieved = ""
buffer = ""
antenaID = ConfigHelper.getAntenaID()
loggerLog.info("[ReciverService][Conf] AntenaId: " + str(antenaID))
loggerLog.info("[ReciverService][Conf] Arrancando receptor...: " + puertoUSB.portstr)

while True:
    try:
        while (puertoUSB.inWaiting() > 0):
            loggerLog.info("[ReciverService][Conf] Dato entrante...")
            buffer = puertoUSB.read(1024)
            loggerLog.info("[ReciverService][Conf] Dato leido: " + buffer)
            loggerLog.info("[ReciverService][Conf] Generando archivo de datos raw...")
            f = open (LOG_PATH, "a")
            loggerLog.info("[ReciverService][Conf] Escribiendo en archivo de datos raw...")
            #Si esta activado el modulo GPS se añade la información al final de la traza
            try:
                isGpsActive=ConfigHelper.isGPSActivo()
                if (isGpsActive):
                    gpsdata = GPSHelper.getGPSDataFromFile()
                    alt = gpsdata[0]
                    lat = gpsdata[1]
                    lon = gpsdata[2]
                    posicionAntena = lat + "," + lon + "|" + alt + "|" + antenaID + "|"
                    loggerLog.info("[ReciverService][Conf] Añadiendo a la traza la ubicación GPS de la antena...")
                    f.write(buffer + posicionAntena)
                #Si no esta activo no se hace nada y se registra tal cual todo lo que se reciva
                else:
                    f.write(buffer + antenaID + "|")
            except Exception as eGps:
                #Si hubiera un error con la captura de datos del GPS en la antena, para asegurar que no se van a perder trazas, se escribe
                #la información entrante en el archivo sin datos de GPS igualmente.
                loggerLog.error("[ReciverService][ERROR] Ha habido un problema con el módulo GPS de la antena " + str(eGps))
                f.write(buffer + antenaID + "|")

            f.close()
            loggerLog.info("[ReciverService][Conf] Archivo de datos raw cerrado")
            buffer = ""

            puertoUSB.flushInput()
            puertoUSB.flushOutput()

    except Exception as e:
        loggerLog.error("[ReciverService][ERROR] " + str(e))
        puertoUSB.close()
        time.sleep(5)

puertoUSB.close()
