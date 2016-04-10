#!/usr/bin/env bash

publish() {
  NAMESPACE=$1
  METRICNAME=$2
  VALUE=$3
  UNIT=$4

  echo publish: $NAMESPACE, $METRICNAME, $VALUE, $UNIT
  aws cloudwatch put-metric-data --metric-name $METRICNAME --namespace $NAMESPACE --value $VALUE --unit $UNIT
}
