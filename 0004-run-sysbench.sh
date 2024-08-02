#!/bin/bash

NAME=$1
LOCAL_PORT=$2
# 43200 seconds is 12 hours, use that when you're ready to run a long test
TIME_SECONDS=$3
THREADS=${4:-$(nproc)}

docker run --network host \
--rm \
--name=$NAME severalnines/sysbench sysbench \
--db-driver=mysql \
--report-interval=2 \
--mysql-table-engine=innodb \
--oltp-table-size=100000 \
--oltp-tables-count=24 \
--threads=$THREADS \
--time=$TIME_SECONDS \
--mysql-host=127.0.0.1 \
--mysql-port=$LOCAL_PORT \
--mysql-user=sbtest \
--mysql-password=password \
/usr/share/sysbench/tests/include/oltp_legacy/oltp.lua run
