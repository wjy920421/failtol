#!/bin/bash

ZOOKEEPER_HOST=$1
SQS_IN=$2
SQS_OUT=$3
WRITE_CAP=$4
READ_CAP=$5
INSTANCES=$6
PROXIED_INSTANCES=$7
BASE_PORT=$8


echo "Zookeepr host: $ZOOKEEPER_HOST "
echo "SQS_IN 	   : $SQS_IN "
echo "SQS_OUT 	   : $SQS_OUT "
echo "WRITE_CAP	   : $WRITE_CAP "
echo "READ_CAP	   : $READ_CAP "
echo "INSTANCE	   : $INSTANCES "
echo "DB Instances : $PROXIED_INSTANCES "
echo "base port add: $BASE_PORT "

IFS=',' read -ra array <<<"$INSTANCES"

for i in "${array[@]}"; do
	#echo $i
	python db.py $ZOOKEEPER_HOST $BASE_PORT $INSTANCES $PROXIED_INSTANCES $SQS_IN $SQS_OUT $WRITE_CAP $READ_CAP
done

#python db.py $ZOOKEEPER_HOST "DB1" $INSTANCES $PROXIED_INSTANCES $BASE_PORT "sub_to" $SQS_IN $SQS_OUT $WRITE_CAP $READ_CAP


python frontend.py $SQS_IN
python backend.py $SQS_OUT