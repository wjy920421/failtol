#!/bin/bash

ZOOKEEPER_HOST=$1
SQS_IN=$2
SQS_OUT=$3
WRITE_CAP=$4
READ_CAP=$5
INSTANCES=$6
PROXIED_INSTANCES=$7
BASE_PORT=$8

IFS=',' read -ra array <<<$INSTANCES

for i in "${array[@]}"; do
	python db.py $ZOOKEEPER_HOST $BASE_PORT $INSTANCES $PROXIED_INSTANCES $BASE_PORT $SQS_IN $SQS_OUT $WRITE_CAP $READ_CAP
done

python frontend.py $SQS_IN
python backend.py $QS_OUT

IFS=',' read -ra array2 <<<$PROXIED_INSTANCES

for i in "${array2[@]}"; do
	python db.py $ZOOKEEPER_HOST $BASE_PORT $INSTANCES $PROXIED_INSTANCES $BASE_PORT $SQS_IN $SQS_OUT $WRITE_CAP $READ_CAP
done