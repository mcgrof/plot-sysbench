#!/bin/bash

NAME=$1
LOCAL_PORT=$2

docker run --network host \
        --rm=true \
        --name=$NAME severalnines/sysbench sysbench \
        --db-driver=mysql \
        --oltp-table-size=100000 \
        --oltp-tables-count=24 \
        --threads=1 \
        --mysql-host=127.0.0.1 \
        --mysql-port=$LOCAL_PORT \
        --mysql-user=sbtest \
        --mysql-password=password \
        /usr/share/sysbench/tests/include/oltp_legacy/parallel_prepare.lua run
