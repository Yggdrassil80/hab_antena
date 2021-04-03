##################################################################################
#Proyecto: rerciverService					                                     #
#Autor: Oscar Loras Delgado				                                         #
#Descricpión: Servicio de recepcion de datos de telemetria de hab_sonda          #
##################################################################################

import os
import glob
import serial
import time
import datetime
import binascii
import logging

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

#Se dejan las configuraciones de prueba para PC
#puertoUSB=serial.Serial('/dev/ttyUSB0',baudrate=9600, timeout = 5.0)
#puertoUSB=serial.Serial('COM4', baudrate=115200, timeout = 5.0)
puertoUSB=serial.Serial(usbRF)
#puertoUSB=serial.Serial('COM4', timeout = 5.0)
#puertoUSB=serial.Serial('COM4')

#Configuración que deberia utilizarse para configurar el chip
#C1C1C1 deberia devolver      C 0  0 0  0 0  1 A  1 7  4 4
#                            6330 3030 3030 3161 3137 3434
#key = ''.join(chr(x) for x in [0xC1, 0xC1, 0xC1])
#print ("key: " + st

#Archivo donde almacenaran los datos recibidos
#LOG_PATH = "/data/hab_antena/logs/recivedData.log"

LOG_PATH = ConfigHelper.getDataFileName()

recieved = ""
buffer = ""
loggerLog.info("[ReciverService][Conf] Arrancando receptor...: " + puertoUSB.portstr)

while True:
    try:
        while (puertoUSB.inWaiting() > 0):
            loggerLog.info("[ReciverService][Conf] Dato entrante...")
            buffer = puertoUSB.read(64)
            loggerLog.info("[ReciverService][Conf] Dato leido: " + str(buffer))
            loggerLog.info("[ReciverService][Conf] Generando archivo de datos raw...")
            f = open (LOG_PATH, "a")
            loggerLog.info("[ReciverService][Conf] Escribiendo en archivo de datos raw...")
            try:
                f.write(str(buffer.decode()))
            except Exception as eGps:
                #Si hubiera un error, se notifica, pero se intenta guardar datos que hubiera en el buffer igualmente
                loggerLog.error("[ReciverService][ERROR] Ha habido un problema con la recepción de los datos: " + str(eGps))
                f.write(str(buffer.decode()))

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
