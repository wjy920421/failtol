#!/bin/bash

ZOOKEEPER_HOST=$1
SQS_IN=$2
SQS_OUT=$3
WRITE_CAP=$4
READ_CAP=$5
INSTANCES=$6
PROXIED_INSTANCES=$7
BASE_PORT=$8


echo "Zookeepr Host     : $ZOOKEEPER_HOST "
echo "SQS_IN            : $SQS_IN "
echo "SQS_OUT           : $SQS_OUT "
echo "WRITE_CAP         : $WRITE_CAP "
echo "READ_CAP          : $READ_CAP "
echo "Instances         : $INSTANCES "
echo "Proxied Instances : $PROXIED_INSTANCES "
echo "Base Port         : $BASE_PORT "

IFS=',' read -ra array <<<"$INSTANCES"

for name in "${array[@]}"; do
    echo "instance name: $name"
    echo "instances: $INSTANCES"
    echo "proxied instances: $PROXIED_INSTANCES"
    python db.py $ZOOKEEPER_HOST $name "$INSTANCES" "$PROXIED_INSTANCES" $BASE_PORT "localhost" $SQS_IN $SQS_OUT $WRITE_CAP $READ_CAP &
done

python frontend.py $SQS_IN &
python backend.py $SQS_OUT &
