export HABLIB_LOGLEVEL=DEBUG #INFO,ERROR
export HABLIB_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
export HABLIB_LOGFILE="/data/hab_antena/logs/hablibclient.log"

python3 -m habmapslib.cli --conffile /data/hab_antena/conf/mqttClient.yaml
