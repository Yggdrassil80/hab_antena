##################################################################################
#Proyecto: localMapService					                                     #
#Autor: Yggdrassil80				                                             #
#Descricpión: Servicio de visualizacion de mapas para hab_sonda                  #
##################################################################################

from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)

import folium
import time
import os
import ConfigHelper
import logging

#Creacion del logger para los logs del servicio
loggerLog = logging.getLogger('server_logger')
loggerLog.setLevel(logging.DEBUG)
inf = logging.FileHandler('/data/hab_antena/logs/localMapService.log')
inf.setLevel(logging.DEBUG)
formatterInformer = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]', datefmt='%Y-%m-%d %H:%M:%S')
inf.setFormatter(formatterInformer)
loggerLog.addHandler(inf)

#Carga de parametros
#Archivo con el directorio donde se encuentran las simulaciones
SIMULATION_PATH = ConfigHelper.getSimulationPath()
#Archivo con los datos en bruto recibidos de la antena
LOG_PATH_RAW = ConfigHelper.getDataFileNameRaw()

# Coordenadas GPS
latitudes = []
longitudes = []

@app.route('/map')
def map():
    #Reiniciar los vectores de latitud y longitud para que no se anadan en los refrescos
    latitudes = []
    longitudes = []
    with open(LOG_PATH_RAW, 'r') as file:
        # Lee las nuevas coordenadas
        new_coordinates = file.readlines()
        if new_coordinates:
            # Actualiza las listas de coordenadas
            for line in new_coordinates:
                ll = line[:-2]
                dataRaw = ll.split('|')
                #122204|2436|42.0266,0.1507|15.7911|40.07|733.6229|2642|5.66|1.015|-0.019|-0.15|130.1718|189.5451|242.6689|7.146|-17.205|-48.543|40.16|15.69|VSP|
                gpsPos = dataRaw[2].split(',')
                lat = float(gpsPos[0])
                lgt = float(gpsPos[1])
                latitudes.append(float(lat))
                longitudes.append(float(lgt))

                #Buscar la latitud mas grande y mas pequena
                latMax = max(latitudes)
                latMin = min(latitudes)
                #Buscar la longitud mas grande y mas pequena
                lonMax = max(longitudes)
                lonMin = min(longitudes)

            # Borra las lineas ya leidas del archivo de texto
            #file.truncate(0)

    # Crear mapa
    locations=[]
    if latitudes:

        m = folium.Map(control_scale=True, zoom_start=6)
        m.fit_bounds([[latMin, lonMin], [latMax, lonMax]])

        #Creacion de capas
        pathVuelo = folium.FeatureGroup("Trayectoria Vuelo")
        
        
        # Calcular capa de trayectoria actual
        locations = list(zip(latitudes, longitudes))
        folium.PolyLine(locations=locations, color='red').add_to(pathVuelo)

        folium.Marker(
            location=[latitudes[0], longitudes[0]],
            popup="Start",
        ).add_to(pathVuelo)

        folium.Marker(
            location=[latitudes[len(latitudes)-1], longitudes[len(longitudes)-1]],
            popup="Actual Position",
            icon=folium.DivIcon(html=f"""<img src="https://static.thenounproject.com/png/5466156-200.png" width="20" height="20">""")
        ).add_to(pathVuelo)

        locations = list(zip(latitudes, longitudes))
        folium.PolyLine(locations=locations, color='red').add_to(pathVuelo)

        listadoSimulaciones = cargarSimulaciones(SIMULATION_PATH)
        #[[[[latData],[lonData]],[burstLat, burstLon],[LandLat, LandLon]]]
        #loggerLog.info(listadoSimulaciones)

        i=0
        for simulacion in listadoSimulaciones:
            #simulacion: [[[latData],[lonData]],[burstLat, burstLon],[LandLat, LandLon]]
            # Definir capa de simulacion
            pathSimul = folium.FeatureGroup("Simulacion " + str(i))
            # Calcular capa de simulacion
            locSimuls = list(zip(simulacion[0][0], simulacion[0][1]))
            folium.PolyLine(locations=locSimuls, color='blue').add_to(pathSimul)

            folium.Marker(
                location=[simulacion[1][0], simulacion[1][1]],
                popup="Estimate Burst",
                icon=folium.DivIcon(html=f"""<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Explosion-155624_icon.svg/2048px-Explosion-155624_icon.svg.png" width="20" height="20">""")
            ).add_to(pathSimul)

            folium.Marker(
                location=[simulacion[2][0], simulacion[2][1]],
                popup="Estimate Landing",
                icon=folium.DivIcon(html=f"""<img src="https://cdn-icons-png.flaticon.com/512/1086/1086043.png" width="20" height="20">""")
            ).add_to(pathSimul)
            #Adicion capas al mapa
            i = i + 1
            pathSimul.add_to(m)
        
        #Adicion capas al mapa
        pathVuelo.add_to(m)
        #Configuracion del control de capas
        folium.LayerControl().add_to(m)

    else:
        m = folium.Map(control_scale=True, zoom_start=6)

    return m._repr_html_()

#####################################################################################

#Metodo que recupera un kml cargado en el path de la aplicacion y asume que corresponde a la simulacion
def cargarSimulaciones(pathBase):
    
    listadoSimulaciones = []

    contenidoSimulaciones = os.listdir(pathBase)

    for simulacion in contenidoSimulaciones:
        loggerLog.info("[localMapService][cargarSimulaciones] Cargando Simulacion " + str(simulacion) + "...");
        datosSim = []
        pathSim = []
        with open(SIMULATION_PATH + simulacion, 'r') as f:
            data = f.read()
        Bs_data = BeautifulSoup(data, "xml")
        coordenadas = Bs_data.coordinates
        aux = coordenadas.string
        aux1 = aux.split('\n')
        latVector = []
        lonVector = []
        for values in aux1:
            if values:
                dataValues = values.split(",")
                latVector.append(round(float(dataValues[1]),5))
                lonVector.append(round(float(dataValues[0]),5))

        pathSim.append(latVector)
        pathSim.append(lonVector)

        #Posicion estimada explosion
        locSimBurst = []
        puntos = Bs_data.find_all("Placemark")
        coord = puntos[2].Point.coordinates.string
        coordenadas = coord.split(",")
        locSimBurst.append(round(float(coordenadas[1]),5))
        locSimBurst.append(round(float(coordenadas[0]),5))

        #Posicion estimada aterrizaje
        locSimLand = []
        puntos = Bs_data.find_all("Placemark")
        coord = puntos[3].Point.coordinates.string
        coordenadas = coord.split(",")
        locSimLand.append(round(float(coordenadas[1]),5))
        locSimLand.append(round(float(coordenadas[0]),5))
        datosSim.append(pathSim)
        datosSim.append(locSimBurst)
        datosSim.append(locSimLand)
        listadoSimulaciones.append(datosSim)
        loggerLog.info("[localMapService][cargarSimulaciones] Simulacion " + str(simulacion) + " cargada OK");

    return listadoSimulaciones

#####################################################################################

if __name__ == '__main__':
    loggerLog.info("[localMapService][Main] Arrancando Mapa Local...");
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    #app.run()
    loggerLog.info("[localMapService][Main] Mapa Arrancado OK");

#####################################################################################





















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

