#!/usr/bin/env bash
. ./publish.sh
VALUE=`ps -elf|wc -l`
UNIT=None
NAMESPACE=ROVER
publish $NAMESPACE 'PROCESSES' $VALUE $UNIT
