#!/usr/bin/env bash
. ./publish.sh
UNIT=Gigabytes
NAMESPACE=ROVER

VALUE=`df -h|grep "\/dev\/root"|awk '{value=($2)} END {print value}'|tr -d "G"`
publish $NAMESPACE 'DISKTOTAL' $VALUE $UNIT

VALUE=`df -h|grep "\/dev\/root"|awk '{value=($3)} END {print value}'|tr -d "G"`
publish $NAMESPACE 'DISKTOTAL' $VALUE $UNIT

VALUE=`df -h|grep "\/dev\/root"|awk '{value=($4)} END {print value}'|tr -d "G"`
publish $NAMESPACE 'DISKTOTAL' $VALUE $UNIT
