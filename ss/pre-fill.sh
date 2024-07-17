#!/bin/bash

# like /dev/nvme0n1
DRIVE=$1
DRIVE_NAME=$(basename $DRIVE)

# Some drives don't have topology information.
BS=131072
QD=129

if [[ -f /sys/block/$DRIVE_NAME/queue/optimal_io_size ]]; then
	BS=$(cat /sys/block/$DRIVE_NAME/queue/optimal_io_size)
fi

if [[ -f /sys/block/$DRIVE_NAME/device/queue_count ]]; then
	QD=$(cat /sys/block/$DRIVE_NAME/device/queue_count)
fi

fio --filename=$DRIVE -direct=1 -name drive-pre-fill \
    --readwrite=write --ioengine=io_uring \
    --blocksize=$BS \
    --iodepth=$QD
