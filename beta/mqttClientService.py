##################################################################################
#Proyecto: mqtt client Service					                 #
#Autor: Yggdrassil80			                         #
#Descricpion: Servicio para el envio de datos recividos a una cola mqtt remota   #
##################################################################################

from habmapslib import MapTracker, HabMapsMessage
import time
import json
from datetime import datetime
import logging
import ConfigHelper
import tail

#Creacion del logger para los logs del servicio
loggerLog = logging.getLogger('server_logger')
loggerLog.setLevel(logging.DEBUG)
inf = logging.FileHandler('/data/hab_antena/logs/mqttClientService.log')
inf.setLevel(logging.DEBUG)
formatterInformer = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]', datefmt='%Y-%m-%d %H:%M:%S')
inf.setFormatter(formatterInformer)
loggerLog.addHandler(inf)

serverHost = ConfigHelper.getMqttServerHost()
serverPort = ConfigHelper.getMqttServerPort()
serverUser = ConfigHelper.getMqttServerUser()
serverPass = ConfigHelper.getMqttServerPass()
dataLogPath = ConfigHelper.getDataFileName()
antennaId = ConfigHelper.getAntennaID()

loggerLog.info("[MQTTClientService][Conf] Mqtt host: " + str(serverHost)) 
loggerLog.info("[MQTTClientService][Conf] Mqtt port: " + str(serverPort))
loggerLog.info("[MQTTClientService][Conf] Mqtt user: " + str(serverUser))
loggerLog.info("[MQTTClientService][Conf] Mqtt pass: " + str(serverPass))
loggerLog.info("[MQTTClientService][Conf] Data Recived File Path: " + str(dataLogPath))
loggerLog.info("[MQTTClientService][Conf] Antenna ID: " + str(antennaId))

def mqtt_sender(traza):

    try:

        mt = MapTracker.MapTracker(id=antennaId, #Nombre de la estacion base
            mqtt_url=serverHost,    #DNS o IP del servidor MQTT
            mqtt_port=int(serverPort),          #Puerto del servidor MQTT
            user=serverUser,          #Credenciales de acceso al broker MQTT
            password=serverPass)

        loggerLog.info("[MqttClientService] cliente mqtt configurado OK")
        mt.startAlive()
        loggerLog.info("[MqttClientService] cliente mqtt arrancado OK")

        loggerLog.info("[MqttClientService] Archivo de datos de antena abierto y leida la primera linea...")

        try:
            loggerLog.info("[MqttClientService] Inicio construccion json de payload a partir de la traza: " + str(traza))
            jsonPayLoad="{"
            trazaTokenized = traza.split("|")
            gpsData = trazaTokenized[2].split(",")

            jsonPayLoad += "\"gpsAlt\"" + ":" + "\"" + trazaTokenized[1] + "\","

            listaCampos = "gpsvelHor temp1 presion bmpAlt IDHAB"
            listaCamposTokenized = listaCampos.split(' ')
            indexCampos = 0
            indexData = 3
            while indexData < 7:
                loggerLog.info("[MqttClientService] nombreCampo: " + str(listaCamposTokenized[indexCampos]))
                loggerLog.info("[MqttClientService] indexData: " + str(indexData))
                if (indexData == 6):
                    jsonPayLoad += "\"" + listaCamposTokenized[indexCampos] + "\"" + ":" + "\"" + trazaTokenized[indexData] + "\""
                else:
                    jsonPayLoad += "\"" + listaCamposTokenized[indexCampos] + "\"" + ":" + "\"" + trazaTokenized[indexData] + "\","
                indexData = indexData + 1
                indexCampos = indexCampos + 1

            jsonPayLoad+="}"
            loggerLog.info("[MqttClientService] PayloadJson creado con valor: " + str(jsonPayLoad))
            loggerLog.info("[MqttClientService] trazaTokenized[0]: " + str(trazaTokenized[0]) + " trazaTokenized[7]: " + str(trazaTokenized[7]))
            loggerLog.info("[MqttClientService] lat y lon: " + str(gpsData[0]) + "," + str(gpsData[1]))

            my_date = datetime.strptime(trazaTokenized[0], "%H%M%S")

            loggerLog.info("[MqttClientService] fecha convertida:" + str(my_date))

            loggerLog.info("[MqttClientService] Inicio envio dato a la mqtt...")
            mt.sendHabMessage(HabMapsMessage.HabMapsMessage(
                TimeStamp=str(my_date), #El timestamp del hab en formato string datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                HabId=trazaTokenized[7], #Nombre del hab que se esta monitorizando, vendra de la traza q transmita el hab
                HabPosition=[gpsData[0], gpsData[1]], #Array de [ latitud, longitud, altura]
                Signals=json.loads(jsonPayLoad),
                BasestationPosition=[gpsData[0], gpsData[1]])) #Array opcional de [ latitud, longitud] de posicion de la estacion base
            loggerLog.info("[MqttClientService] Dato enviado OK!")
        except Exception as e2:
            loggerLog.error("[MqttClientService] Se ha producido un error, se sigue iterando: " + str(e2))
            time.sleep(5)
        loggerLog.info("[MqttClientService] Lectura de la siguiente traza")

    except Exception as e1:
        loggerLog.error("[MqttClientService] Se ha producido un error, se sigue iterando: " + str(e1))
        time.sleep(2)

t = tail.Tail(dataLogPath)
t.register_callback(mqtt_sender)
t.follow(s=5)
