#!/usr/bin/env bash
. ./publish.sh
VALUE=`cat /proc/sys/fs/file-nr |awk '{open=($1)} END {print open}'`
UNIT=None
NAMESPACE=ROVER
publish $NAMESPACE 'OPENFILES' $VALUE $UNIT
