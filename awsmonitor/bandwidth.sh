#!/usr/bin/env bash
START=`cat /proc/net/dev|grep wlan0|awk '{bytes=($2)} END {print bytes}'`

sleep $1

END=`cat /proc/net/dev|grep wlan0|awk '{bytes=($2)} END {print bytes}'`

DIFF=`expr $END - $START`

echo $DIFF
