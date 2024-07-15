#!/bin/bash
NAME="$1"

docker exec -it $NAME /root/post-entrypoint-custom-bringup.sh
