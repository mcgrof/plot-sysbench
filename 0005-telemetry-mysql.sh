#!/bin/bash
 
NAME=$1
# 720 minutess in 12 hours, first try with just one minute
TIME_MINUTES=$2
 
	#-e PYTHONPATH="$PYTHONPATH:/usr/local/lib/python3.9/site_packages/" \
docker exec -it \
	$NAME \
	mysqlsh  -u root -pmy-secret-pw --execute "support.collect(mysql=true, os=true, time=$TIME_MINUTES, outputdir='/opt/')"
