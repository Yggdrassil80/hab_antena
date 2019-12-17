#!/usr/bin/python
import serial
import time
import datetime
import binascii

usbRF = ConfigHelper.getUsbRF()

#puertoUSB=serial.Serial('/dev/ttyUSB0',baudrate=9600, timeout = 5.0)
#puertoUSB=serial.Serial('COM4', baudrate=115200, timeout = 5.0)
puertoUSB=serial.Serial(usbPort)
#puertoUSB=serial.Serial('COM4', timeout = 5.0)
#puertoUSB=serial.Serial('COM4')

#C1C1C1 deberia devolver      C 0  0 0  0 0  1 A  1 7  4 4
#                            6330 3030 3030 3161 3137 3434
#key = ''.join(chr(x) for x in [0xC1, 0xC1, 0xC1])
#print ("key: " + st

LOG_PATH = "/data/hab_antena/logs/recivedData.log"

recieved = ""
buffer = ""

print("[RFLora] Arrancando receptor..." + puertoUSB.portstr)

while True:

    while (puertoUSB.inWaiting() > 0):
        print("[RFLora] Dato entrante...")
        buffer = puertoUSB.read(1024)
        print ("[RFLora] Dato leido: " + buffer)
        print("[RFLora] Generando archivo de datos raw...")
        f = open (LOG_PATH, "a")
        print("[RFLora] Escribiendo en archivo de datos raw...")
        f.write(buffer)
        f.close()
        print("[RFLora] Archivo de datos raw cerrado")
        buffer = ""

        puertoUSB.flushInput()
        puertoUSB.flushOutput()

puertoUSB.close()
