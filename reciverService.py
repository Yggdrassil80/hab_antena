##################################################################################
#Proyecto: rerciverService					                                     #
#Autor: Yggdrassil80				                                         #
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

#Archivo donde almacenaran los datos recibidos
LOG_PATH = ConfigHelper.getDataFileName()
LOG_PATH_RAW = ConfigHelper.getDataFileNameRaw()

recieved = ""
buffer = ""
loggerLog.info("[ReciverService][Conf] Arrancando receptor...: " + puertoUSB.portstr)


encontrado = 0
traza = ""
newTraza = ""
trozoFinal = bytearray()
trozoNoFinal = bytearray()

while True:
    try:
        while (puertoUSB.inWaiting() > 0):
            loggerLog.debug("[ReciverService] Dato entrante...")
            buffer = puertoUSB.read(128)
            loggerLog.debug("[ReciverService] Dato leido: " + str(buffer))
            loggerLog.debug("[ReciverService] Generando archivo de datos raw...")
            fraw = open (LOG_PATH_RAW, "a")
            fraw.write(buffer.decode())
            fraw.close()
            loggerLog.debug("[ReciverService] Archivo de datos en raw cerrado")
            loggerLog.debug("[ReciverService] Generando archivo de datos para mqtt...")
            for i in range(len(buffer)):
                 if (buffer[i] == 10):
                     #salto de carro encontrado, los datos van de i=0 a i.
                     encontrado = 1
                     trozoFinal = buffer[0:i+1]
                     trozoNoFinal = buffer[i+1:len(buffer)] 
                     loggerLog.debug("[ReciverService] byte leido: " + str(buffer[i]) + " en posicion: " + str(i))
                     break

            if (encontrado == 1): 
                #Existe un trozo final
                traza+=trozoFinal.decode()
                newTraza = trozoNoFinal.decode() 
                f = open (LOG_PATH, "a")
                loggerLog.debug("[ReciverService] Fragmento final recuperado:" + trozoFinal.decode())
                loggerLog.debug("[ReciverService] Escribiendo en archivo de datos para mqtt...")
                loggerLog.info("[ReciverService] traza a escribir: " + str(traza))
                try:
                    f.write(traza)
                except Exception as eGps:
                    #Si hubiera un error, se notifica, pero se intenta guardar datos que hubiera en el buffer igualmente
                    loggerLog.error("[ReciverService][ERROR] Ha habido un problema con la recepción de los datos: " + str(eGps))
                    f.write(traza)
                f.close()
                loggerLog.debug("[ReciverService] Archivo de datos cerrado")
                traza = newTraza
                newTraza = ""
                encontrado = 0
                loggerLog.info("[ReciverService] Fragmento inicial de traza: " + traza)
            else:
                trozoNoFinal = buffer[0:len(buffer)]
                loggerLog.debug("[ReciverService] Fragmento recuperado:" + trozoNoFinal.decode())
                traza+=trozoNoFinal.decode()
                loggerLog.info("[ReciverService] Traza actual: " + traza)

            loggerLog.debug("[ReciverService] traza vale: " + traza + " newTraza vale: " + newTraza)

            buffer = ""
            puertoUSB.flushInput()
            puertoUSB.flushOutput()

    except Exception as e:
        loggerLog.error("[ReciverService][ERROR] " + str(e))
        puertoUSB.close()
        time.sleep(5)

puertoUSB.close()
