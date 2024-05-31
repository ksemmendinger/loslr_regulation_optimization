#!/bin/bash

loc="$1"                # home directory for the optimization code
config="$2"             # path to config file from home directory
nseeds="$3"              # number of random seeds to run optimization

SEEDS=$(seq 1 ${nseeds})
for S in ${SEEDS}
do
echo python optimizationWrapper.py ${loc} ${config} ${S}
done
wait < <(jobs -p)