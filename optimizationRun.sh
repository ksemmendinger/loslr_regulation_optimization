#!/bin/bash

loc="$1"                # home directory for the optimization code
config="$2"             # path to config file from home directory
SEEDS="$3"              # number of random seeds to run optimization

for S in ${SEEDS}
do
python optimizationWrapper.py ${loc} ${config} ${S}
done
wait < <(jobs -p)