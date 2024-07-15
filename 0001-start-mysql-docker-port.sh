#!/bin/bash

NAME=$1
CNF=$2
LOCAL_PORT=$3
MYSQL_DIR=$4
TELEMETRY_DATA_DUMP=${5:-/opt/mysql-sysbench-telemetry/}
MYSQL_ROOT_USERDIR=${6:-/opt/root-user/}

docker run \
      --rm \
      --name $NAME \
      --volume=$CNF:/etc/mysql/conf.d/mysql.cnf \
      --volume=$MYSQL_DIR:/var/lib/mysql \
      --volume=$TELEMETRY_DATA_DUMP:/opt/ \
      --volume=$MYSQL_ROOT_USERDIR:/root/ \
      -p $LOCAL_PORT:3306 \
      -e MYSQL_DATABASE=sbtest \
      -e MYSQL_ROOT_PASSWORD=my-secret-pw \
      -e PYTHONPATH=/usr/local/lib/python3.9/site-packages \
      -d mysql:8.0
