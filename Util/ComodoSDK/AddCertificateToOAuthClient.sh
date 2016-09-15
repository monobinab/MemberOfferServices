dt=`date +"%m-%d-%Y-%H-%M"`
java -cp "CLASSES:.:/home/auto/vmathu0/qa/ComodoSDK/jars/commons-codec-1.2.jar:/home/auto/vmathu0/qa/ComodoSDK/jars/commons-httpclient-3.1.jar:/home/auto/vmathu0/qa/ComodoSDK/jars/commons-logging-1.0.4.jar:/home/auto/vmathu0/qa/ComodoSDK/jars/log4j-1.2.16.jar:/home/auto/vmathu0/qa/ComodoSDK/jars/ComodoCertManager_v1.4.6.jar" com.sears.telluride.security.comodo.ComodoClientMain $1 /home/auto/vmathu0/qa/ComodoSDK/configs/comodo_config_TELLQA.properties $2 $3 > /home/auto/vmathu0/qa/ComodoSDK/logs/$1_$dt.log

