#!/bin/bash

loc="$1"        # home directory for the optimization code
config="$2"     # path to config file from home directory
nseeds="$3"     # number of random seeds to run optimization

# array of unique seeds based on number of seeds specified
SEEDS=$(seq 1 ${nseeds}) 

# for loop to run optimizationWrapper.py for each seed
for S in ${SEEDS} 

do
python optimizationWrapper.py ${loc} ${config} ${S}
done

# tells shell script to wait to exit until all the seeds are done running
wait < <(jobs -p) 