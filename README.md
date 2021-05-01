- [HAB_antena](#hab-antena)
  * [Introducción](#introducci-n)
  * [Diagrama de sistemas](#diagrama-de-sistemas)
  * [Getting Started](#getting-started)
  * [Configuraciones Genericas](#configuraciones-genericas)
    + [Generación de Servicios](#generaci-n-de-servicios)
    + [Activación I2C en Raspbian](#activaci-n-i2c-en-raspbian)
    + [Configuración USBs](#configuraci-n-usbs)
  * [Logging](#logging)
  * [Descripción Componentes](#descripci-n-componentes)
    + [GPS](#gps)
    + [RF](#rf)
    + [Proceso HabMap](#proceso-HabMap)
    + [Servicio de Configuración](#servicio-de-configuraci-n)
  * [Hardware](#hardware)
    + [Diagrama del Hardware](#diagrama-del-hardware)
    + [Bus I2C](#bus-i2c)
    + [USBs](#usbs)
    + [Listado de componentes](#listado-de-componentes)
    + [Tecnicas y procedimientos de ensamblado](#tecnicas-y-procedimientos-de-ensamblado)

# HAB_antena

Proyecto para implementar el software de captura y procesamiento de datos de una sonda HAB que emita con LoRa

## Introducción

En este proyecto se describirán los principales componentes de la antena receptora del proyecto hab_sonda.

## Diagrama de sistemas

![diagrama_sistemas_antena](docs/images/diagrama_sistemas_antena.png)

## Getting Started

Este apartado esta pensado para, sin tener el detalle exacto de todos los componentes y tecnicas que se explican mas adelante, poner en funcionamiento el software de la antena.

Los pasos son:

1. Disponer de una raspberry Pi con una versión de raspbian instalada y funcionando correctamente. Ejecutar antes de nada:

```
sudo apt get update
```

2. Descargar git para poder descargar posteriormente el código de la sonda

```
sudo apt install git
```

3. Conectar todos los sistemas periféricos (gps y Lora(rf) principalmente)

4. Instalar librerias de Python3 de apoyo. Las librerias de python necesarias son las siguientes:
   * scipy
   * ...
   
y la forma de instalarlas es mediante la instrucción
```
   pip3 install [nombre_libreria]
```

5. Crear el directorio de trabajo, data, mediante las siguientes instrucciones. 

<b>IMPORTANTE:</b> Todas las rutas de configuración estan pensadas sobre este directorio, no se recomienda cambiar a no ser que se tenga muy claro que deberá revisarse ben todo el código para reemplazar este directorio base por cualquier otro que se escoja.

```
cd /
mkdir data
sudo chown -R pi:pi data/
sudo chmod -R 777 data/
```

6. Realizar un clone del proyecto hab_antena sobre la raspberry
   El proceso es simple.
   1. Abrir una consola del SO.
   2. Posicionarse en el directorio que se desee (se recomienda /data)
   3. Ejecutar la instrucción de clonado del repositorio "hab_antena" con el comando:
```
git clone https://github.com/Yggdrassil80/hab_antena
```
<b>IMPORTANTE</b>: Inmediatamente despúes de realizar esta accion, todo el código de la antena se encontrará en /data/hab_antena. Esto implica que todas las configuraciones dependeran de ese path base.

7. Crear el directorio de logs, mediante la instruccion

```
cd /data/hab_antena
mkdir logs
```

8. Configurar los archivos de configuración.
   1. Para realizar esta acción se ha de configurar el archivo /data/hab_antena/conf/tracker.conf
   2. Los detalles de configuración de cada sensor se pueden consultar en la sección de configuración de cada módulo descritos en la sección [Componentes](#componentes)
   3. Lo siguiente será configurar el archivo mqttClient.yaml. Los detalles de este archivo se encuentran en la sección

* NOTA *: Llegado es punto, si se deseara, se puede cambiar el nombre "hab_antena" por el nombre que se desee. Esto se puede hacer utilizando los comandos siguiente:

```
cd /data/hab_antena
grep -rli 'hab_antena' * | xargs -i@ sed -i 's/hab_antena/nombre_nuevo/g' @
```

Para que los cambios no provoquen errores de configuración, todo el directorio de configuración debería cambiar también a /data/nombre_nuevo

Esto se puede hacer utilizando el comando:

```
mv -rf /data/hab_antena /data/nombre_nuevo
```

9. Configurar y activar los servicios. Ver el punto [Generación de Servicios](#generaci-n-de-servicios)

## Configuraciones Genericas

### Generación de Servicios

Como se ha indicado, la idea es que cada componente nuevo que se agrege, se conciba como un servicio que se ejecute en el arranque de la pi en un orden preestablecido y con las dependencias que se desee.

En el código descargado de git ya se dispone de los diferentes archivos .service preparados para ser arrancados localmente. Es importante que se arranques los servicios de este modo, ya que esto asegura que al encender la pi o tras su reinicio, estos servicios se activen <b>automáticamente</b>.

Para poder arrancar el servicio de un componente:

1. Se debe disponer del archivo [Nombre_modulo.service] donde se ha de describir, genericamente, lo siguiente:

```
[Unit]
Description=[nombre_en_systemctl_del_servicio]
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /[path_hubicación_proceso_python_arranque_servicio]/[nombre_servicio].py
Restart=always
RestartSec=0

[Install]
WantedBy=multi-user.target
```

2. Copiar el archivo del servico al directorio de systemd
```
sudo cp [nombre_servicio].service /etc/systemd/system/[nombre_servicio].service
```

3. Refrescar la lista de servicios y activar el nuevo que se desea dar de alta.
```
sudo systemctl daemon-reload
sudo systemctl enable [nombre_servicio].service
```

<b>IMPORTANTE</b>: Asegurarse que el script de python definido en el [Nombre_modulo.service] tiene permisos de ejecución (chmod 755)

4. Finalmente, para arrancar o parar el servicio una vez la el SO haya arrancado, utilizar.
```
sudo systemctl start [nombre_servicio].service

o

sudo systemctl stop [nombre_servicio].service
```

### Activación I2C en Raspbian

Los componentes que necesita la antena no requieren configuración del bus I2C.

### Configuración USBs

Todos los puertos usbs, una vez conectados, están disponibles, como si fueran un archivo, en la raspberry en el directorio /dev.

Normalmente, vienen descritos como

- ttyUSB0
- ttyUSB1
...

Para poder configurarlos en el archivo de configuración, para configurar el RF o el GPS, deberá situarse en la variable correspondiente el path absoluto de estos archivos.

- /dev/ttyUSB0
- /dev/ttyUSB1
...

## Logging

TODO

## Descripción Componentes

### GPS

#### Introducción

El GPS, permite determinar la ubicación exacta de la antena. La configuración de este módulo para la antena no es imprescindible, pero otorga la posibilidad de añadir las coordenadas GPS de la antena que recibió los datos e incorporarlos en la traza capturada. Esto puede ser muy util para determinar distancias reales de recepción o que condiones atmosfericas alteraron o no la misma por ejemplo.

#### Descripción

El GPS sobre el cual se basado este desarrollo es el UBLOX NEO 6M que también se ha demostrado compatible con el UBLOX NEO 7.

Lo que se desea del GPS es que retorne constantemente la altura, la latitud y la longitud de la antena. Estos datos son solo unos de los pocos que se pueden extraer del GPS.

Actualmente, los chips de UBLOX operan con protocolo NMEA2.0 que se basa en la generación de una série de mensajes con datos de tiempos, velocidades, posiciones, etc.

Se puede encontrar mas información aqui: https://www.gpsinformation.org/dale/nmea.htm

Se ha desarrollado un módulo propio que interpreta los mensajes NMEA que se consideran interesantes para conocer los datos de altura, longitud y latitud de la antena (GCRMC y el GCACC).

#### Conexión 

Los chips de ublox estan configurados para empezar a volcar sus datos directamente por el puerto serie. Con un simple adaptador a USB (CP2102) se puede utilizar practicamente desde cualquier sistema operativo o plataforma que soporte USB.

#### Calibrado

Este componente no requiere ninguna acción de calibrado especial, ya que tras el encendido empieza a calcular su posición el solo. Para ganar una precisión adecuada de pocos metros, si hace mucho que no se usa, puede requerir unos minutos (5 o 10 min).

#### Configuración

A diferencia de otros componentes, los chips de UBLOX de GPS requieren de configuración inicial dependiendo de lo que se desee hacer con ellos.

En nuestro caso, nuestra aplicación implica que se alcanzaran alturas de entre 30 a 40km en el mejor de los casos, y practicamente ningun GPS convencional mide tales alturas de fabrica.

Además, existe un organismo internacional, COCOM que limita la altura a la cual estos sistemas civiles pueden operar. Nominalmente esta en 18km como maximo, pero dependendiendo del fabricante hay limites en 9 o 12km.

Superado este limite, el comportamiento del componente es diverso, en función del fabricante. En el caso de UBLOX, los datos de lat, lon y altura se quedan "congelados" hasta que se recupera una altura inferior a la del límite de configuración.

Para solventar esto, el componente de GPS desarrollado implementa una libreria especial que permite la configuración de GPS de UBLOX mediante su protocolo de comunicaciones de fabricante (UBX). Luego, cada vez que se arranca el módulo de GPS, se lanza una configuración que activa el modo "airbone<1g" que permite la operación del chip hasta alturas de 50km.

Otras configuraciones adicionales son aplicadas también, como el filtrado de paquetes de NMEA, para solo capturar los GCRMC y GCACC.

Adicionalmente, también existen configuraciones estáticas en el archivo conf/hav.conf

usbGPS=/dev/ttyUSB0
tiempoMuestreoGPS=10

donde,

- usbGPS: corresponde al puerto USB al que esta conectado el adaptador cp2102 del GPS. Es importante destacar que este puerto puede cambiar en función de los dispositivos conectados a la raspberry y el slot USB donde se conecten, con lo que se deberá comprobar manualmente que esta configuración es correcta.
- tiempoMuestreoGPS: que informa sobre el tiempo entre muestras de datos de GPS. Es importante destacar que el GPS no empieza a dar datos de posición de forma inmediata cuando arranca, sino que requeriere unos minutos de "autocalibrado" antes de empezar a recibir paquetes NMEA con datos (GCRMC y GCACC). Luego, suponiendo la configuración correcta de USB, se puede entender como normal que no haya datos de posición nada mas arrancar.

Finalmente, recordar que el uso de este módulo en la antena otorga la capacidad de disponer, en la misma traza recibida, de las coordenadas GPS + altura del HAB y de la antena a la vez, con lo que, eventualmente, se podría calcular la distancia real exacta entre antena y HAB.

### Servicio de Recepcion

#### Introducción

En este caso, el módulo de recepción se denomina reciverService y es el encargado de permanecer escuchando las trazas entrantes del HAB.

#### Descripción

Este servicio basa su funcionamiento en un chip de RF Ebyte-E32-TTL-100 que viene ya preconfigurado de fabrica. Se conecta a la raspberry a través del puerto serie y, mediante un adaptador CP2102, a un slot USB.

Dispone además de dos pines de configuración, M0 y M1 que, para que pueda funcionar en modo recepción y emisión han de estar a 0V (ojo, no en Z).Osea, conectados al GND de la PI.

Para poder configurar los parametros internos del chip M0 y M1 han de configurarse ambos a 1 lógico (3.3V).

Toda la configuración los parametros de LoRa del chip se basa en el parametro de airrate que viene a ser el ancho de banda con el que transmite el chip.

Los siguientes parámetros de configuración de LoRa son los que corresponden a cada airRate.

 - 0.3 Kbps, BW:125Mhz, SF: 12, CR: 4/5
 - 1.2 Kbps, BW:250Mhz, SF: 11, CR: 4/5
 - 2.4 Kbps, BW:500Mhz, SF: 12, CR: 4/5
 - 4.8 Kbps, BW:250Mhz, SF: 8, CR: 4/6
 - 9.6 Kbps, BW:500Mhz, SF: 8, CR: 4/6
 - 19.2 Kbps, BW:500Mhz, SF: 7, CR: 4/6

 donde,

 - BW: Significa BandWith
 - SF: Spread Factor
 - CR: Coding Rate

La frecuencia central se encuentra en los 433 Mhz.

El airRate por defecto es de 2.4 Kbps. Es decir, la velocidad de transferencia del chip.

El modulo de software desarrollado para este chip aisla todos estos elementos de configuración del desarrollador. 

Un aspecto interesante de este módulo es que genera dos archivos, cuyo nombre es configurable, pero inicialmente estan denominados como recivedData.log y recivedDataRaw.log. El primero es un archivo procesado donde se garantiza que las trazas recibidas se escriben de linea en linea (incluyendo el salto de carro) de forma que el servicio de mapas pueda procesar linea a linea el archivo de forma mas eficiente.

El segundo archivo es el recivedDataRaw.log. Este archivo corresponde a la información en Raw que llega directamente desde la antena. Se almacena asi por seguridad, para evitar que un posible error en el procesado de datos para la libreria de mapas pueda hacer perder algún dato.

#### Configuración

Existe configuración estática para este modulo en el archivo de configuración conf/tracker.conf, dentro del tag [RF] y dentro del tag [TCK]

En RF:
```
usbRF=/dev/ttyUSB2
```
donde,

- usbRF: corresponde al puerto USB al que esta conectado el adaptador cp2102 del componente de RF (Lora ebyte). Es importante destacar que este puerto puede cambiar en función de los dispositivos conectados a la raspberry y el slot USB donde se conecten, con lo que se deberá comprobar manualmente que esta configuración es correcta.

<b> IMPORTANTE: </b> Para que exista comunicación entre dos componentes de este tipo, ambos han de estar configurados en la misma frequencia y canal.

En TCK:
```
dataPath=/data/hab_antena/logs/recivedData.log
dataPathRaw=/data/hab_antena/logs/recivedDataRaw.log
```

donde,
- dataPath: corresponde al archivo donde se dejaran los datos recibidos y preparados para ser consumidos por el servicio de mapas
- dataPathRaw: que corresponde al archivo de datos recibidos en raw por parte de la antena.

### Proceso HabMap

#### Introducción

Este módulo de software es el encargado de coger los datos recibidos por la antena y llevarlos a una cola mqtt en la nube (o donde se desee). En el proceso enriquecerá los datos recibidos con un identificador de antena y la posición GPS de la misma, si este servicio estuviera configurado. 

#### Descripción

Este componente basa su funcionamiento en una libreria desarrollada para tal efecto que es preciso instalar.

<b>NOTA: </b> Para mas información sobre detalles de funcionamiento, instalación y configuración de esta libreria se pueden encontrar aquí: https://pypi.org/project/habmapslib/ 

La instalación de la libreria se efectúa mediante la siguiente instrucción:

```
sudo pip3 install habmapslib
```

La libreria esta pensada para poder ser arrancada como un servicio mas de raspbian. El ejecutable que gobierna su servicio de arranque es el archivo /data/hab_antena/habMapService.sh.

El servicio que arranca la libreria tiene un archivo .service en /data/hab_antena/services que es instalable a partir de lo explicado en los puntos superiores de este documento o bien utilizando las tools disponinbles en el directorios de /utilities.

#### Configuración

La configuración de este componente se realiza  través de un archivo de configuración adicional, denominado por defecto mqttClient.yaml que tiene el contenido por defecto siguiente:

```
basestation:
  id: "HABANTENA01"
  appenders:
    gpsappender:
      file: '/data/hab_antena/logs/gpsdata.log'
      regexselect: '\[.*\]\|(.*)\|(.*),(.*)\|.*\|'
      mapping:
        - "height"
        - "lat"
        - "lon"
mqtt:
  url: "localhost"
  topic: "hablistener"
  port: 1883
  user: "habmaps"
  password: "root"
  alive: 60
frame:
  # Definición de la trama donde
  # $time : Es la hora expresada en HHMMSS
  # $pos : Es la posición gps del hab expresada en lat,lon
  # $id  : Es el identificador del hab
  format: "$time|AlturaGPS|$pos|VelocidadHorizontalGPS|Temperatura|Presion|AlturaBarometrica|$id|"
  # Fichero donde se van insertando las trazas de LoRa
  file: "/data/hab_antena/logs/recivedData.log"
  # Cada cuantos segundos se mira el fichero de envio
  refresh: 1
```

La configuración de este archivo difiere de la configuración tradicional que se puede observar en el tracker.conf, donde la configuración es de tipo clave=valor.

Aqui se ha desarrollado vía yaml, que es un estandar de representación de archivos similar al xml.

Los campos a configurar son:
- basestation.id: identificador de la antena. Es una etiqueta que identificará, para cada traza recibida, que antena la ha recivido.
- basestation.appender.: Contiene la información necesaria para procesar la información del servicio de GPS que pudiera estar configurado en la antena. <b>No es preciso alterar esta configuración<b>
- mqtt.utl: Su valor por defecto es localhost, pero en funcionamiento real corresponderá a la url del servidor remoto donde se encuentre la cola mqtt que almacenará los datos que se le envien desde la antena. <b> Este valor será proporcionado el dia del lanzamiento a los responsables de su configuración <b>
- mqtt.topic: Los servidores mqtt disponen de colas o topics donde se pueden escribir los datos y leerlos posteriormente. En el caso particular de la libreria que se ha creado, tiene el valor "hablistener" y <b>no es preciso alterarlo</b>
- mqtt.port: Valor por defecto del puerto donde se encuentre levantado el servidor mqtt en la nube. Su valor es "1883" y <b>no es preciso alterarlo</b>
- mqtt.user: Para securizar la solución de la cola mqtt y evitar que nadie mas que las antenas publiquen datos en el, se ha creado un usuario y un password para proteger la ingesta de datos. Su valor por defecto es "habmaps" pero <b>se proporcionará uno específico para el dia del lanzamiento</b>
- mqtt.password: Valor por defecto "root". Corresponde al password del usuario anterior.
- mqtt.alive: Valor por defecto "60". <b>No es necesario manipular".

### Servicio de Configuración

#### Introducción

El sistema de configuración es un módulo de soporte que se encarga de recuperar los datos de configuración del archivo de configuración que se le configure.

Ayuda a hacer mas mantenible el código y a una mejor parametrización del software.

#### Descripción

Se basa en una libreria interna de python denominada "configparser" que es capaz de leer configuraciones del tipo:

```
[nombre_seccion1]
param11=valor11
...
param1N=valor1N
....
[nombre_seccionM]
paramM1=valorM1
paramMZ=valorMX
```

Para cada nuevo parámetro que se dese añadir al archivo de configuración se ha de crear un método de lectura en este módulo.

## Hardware

### Diagrama del Hardware
TODO
### Bus I2C
TODO
### USBs
TODO
### Listado de componentes
TODO
### Tecnicas y procedimientos de ensamblado
TODO

