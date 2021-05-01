#!/usr/bin/python

import configparser
import logging

#loggerLog = logging.getLogger('server_logger-config')
#loggerLog.setLevel(logging.INFO)
#inf = logging.FileHandler('/data/hab_sonda/logs/wsp-Config.log')
#inf.setLevel(logging.INFO)
#formatterInformer = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]', datefmt='%Y-%m-%d %H:%M:%S')
#inf.setFormatter(formatterInformer)
#loggerLog.addHandler(inf)

CONF_PATH = "/data/hab_antena/conf/tracker.conf"

def getMqttServerHost():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("MQTT", "mqttHost")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "valor vacio"

def getMqttServerPort():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("MQTT", "mqttPort")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "valor vacio"

def getMqttServerUser():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("MQTT", "mqttUser")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "valor vacio"

def getMqttServerPass():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("MQTT", "mqttPass")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "valor vacio"

def getAntennaID():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("TCK", "antenaID")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "valor vacio"

def getDataFileNameRaw():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("TCK", "dataPathRaw")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "defectID"


def getDataFileName():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("TCK", "dataPath")
        return str(t)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaID] ERROR");
        return "defectID"

def getTiempoEntreMov():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("TCK", "tiempoEntreMov")
        return int(t)
    except:
        #loggerLog.error("[ConfigHelper][getTiempoEntreMov] ERROR");
        return "valor vacio"

#Metodo que recupera la posición de la antena de la configuracion (se asume antena estática y sin módulo GPS)
def getAntenaPos():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        lat = cfg.get("GPS", "lat")
        lon = cfg.get("GPS", "lon")
        alt = cfg.get("GPS", "alt")
        return float(lat), float(lat), int(alt)
    except:
        #loggerLog.error("[ConfigHelper][getAntenaPos] ERROR");
        return [0.0, 0.0, 0]

#Metodo que informa sobre el estado de activacion del MPU
def isMPUActivo():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("MPU", "mpu_activo")
        return int(t)
    except:
        #loggerLog.error("[ConfigHelper][isMPUActivo] ERROR");
        return "valor vacio"

#Metodo que informa sobre el estado de activacion de la brujula
def isORIActivo():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("ORI", "ori_activo")
        return int(t)
    except:
        #loggerLog.error("[ConfigHelper][isORIActivo] ERROR");
        return "valor vacio"

#Metodo que informa sobre el estado de activacion del MPU
def isGPSActivo():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("GPS", "gps_activo")
        return int(t)
    except:
        #loggerLog.error("[ConfigHelper][isGPSActivo] ERROR");
        return "valor vacio"

#Metodo que recupera el tiempo de muestreo del MPU
def getTiempoMuestreoMPU():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("MPU", "tiempoMuestreoMPU")
        return int(t)
    except:
        #loggerLog.error("[ConfigHelper][getTiempoMuestreoMPU] ERROR");
        return "valor vacio"

#metodo que recupera el tiempo de muestreo del GPS
def getTiempoMuestreoGPS():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        t = cfg.get("GPS", "tiempoMuestreoGPS")
        return int(t)
    except:
        #loggerLog.error("[ConfigHelper][getTiempoMuestreoGPS] ERROR");
        return "valor vacio"

#Metodo que recupera el puerto del usb de RF
def getUsbRF():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        puerto = cfg.get("RF", "usbRF")
        return puerto
    except:
        #loggerLog.error("[ConfigHelper][getUsbRF] ERROR");
        return "Puerto Vacio"

#Metodo que recupera el puerto del usb de GPS
def getUsbGPS():
    try:
        cfg = configparser.ConfigParser()
        cfg.read([CONF_PATH])
        puerto = cfg.get("GPS", "usbGPS")
        return puerto
    except:
        #loggerLog.error("[ConfigHelper][getUsbGPS] ERROR");
        return "Puerto Vacio"

