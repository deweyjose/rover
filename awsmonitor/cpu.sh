#!/usr/bin/env bash
. ./publish.sh
CPUUSAGE=`grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}'`
publish 'ROVER' 'CPU%' $CPUUSAGE 'Percent'

