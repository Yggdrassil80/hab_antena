#!/bin/bash

export HABLIB_LOGLEVEL=DEBUG #INFO,ERROR
export HABLIB_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
export HABLIB_LOGFILE="/data/hab_antena/logs/hablibclient.log"

/usr/bin/python3 -m habmapslib.cli --conffile /data/hab_antena/conf/mqttClient.yaml
